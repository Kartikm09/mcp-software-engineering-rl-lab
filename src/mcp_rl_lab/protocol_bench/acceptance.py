"""Trusted evaluator-side behavior checks; this file is never copied to candidates."""

import ast
import asyncio
import contextlib
import importlib.util
import json
import sys
from pathlib import Path


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def raises(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError("required ValueError was not raised")


async def duplicate(module, case):
    coordinator = module.Coordinator()
    if case == "same-key-effect-and-cache":
        entered = asyncio.Event()
        release = asyncio.Event()
        calls = []

        async def effect():
            calls.append(1)
            entered.set()
            await release.wait()
            return 42

        left = asyncio.create_task(coordinator.run("a", effect))
        await entered.wait()
        right = asyncio.create_task(coordinator.run("a", effect))
        # A scheduler turn, not a wall-clock sleep, exposes overlapping requests.
        await asyncio.sleep(0)
        release.set()
        require(await left == await right == 42, "shared result differs")
        require(
            await coordinator.run("a", effect) == 42 and len(calls) == 1, "duplicate side effect"
        )
    elif case == "different-keys-progress":
        entered = asyncio.Event()
        release = asyncio.Event()

        async def slow():
            entered.set()
            await release.wait()
            return "a"

        async def fast():
            return "b"

        left = asyncio.create_task(coordinator.run("a", slow))
        await entered.wait()
        right = asyncio.create_task(coordinator.run("b", fast))
        for _ in range(8):
            await asyncio.sleep(0)
        independent = right.done() and right.result() == "b"
        release.set()
        await left
        await right
        require(independent, "different keys blocked or coalesced")
    elif case == "failed-work-retry":

        async def failed():
            raise ValueError("controlled failure")

        async def recovered():
            return 7

        try:
            await coordinator.run("a", failed)
        except ValueError:
            pass
        else:
            raise AssertionError("controlled failure swallowed")
        try:
            value = await coordinator.run("a", recovered)
        except ValueError as error:
            raise AssertionError("failed work poisoned retry") from error
        require(value == 7, "retry did not recover")
    elif case == "failed-effect-after-waiter-cancel-can-retry":
        entered = asyncio.Event()
        release = asyncio.Event()

        async def fails_later():
            entered.set()
            await release.wait()
            raise ValueError("controlled delayed failure")

        async def recovered():
            return 9

        waiter = asyncio.create_task(coordinator.run("a", fails_later))
        await entered.wait()
        waiter.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await waiter
        release.set()
        for _ in range(8):
            await asyncio.sleep(0)
        try:
            result = await coordinator.run("a", recovered)
        except ValueError as error:
            raise AssertionError("orphaned failed effect poisoned the next retry") from error
        require(result == 9, "post-cancellation retry did not recover")
    elif case == "cancelled-waiter-does-not-cancel-shared-effect":
        entered = asyncio.Event()
        release = asyncio.Event()
        calls = []

        async def effect():
            calls.append(1)
            entered.set()
            await release.wait()
            return 8

        left = asyncio.create_task(coordinator.run("a", effect))
        await entered.wait()
        right = asyncio.create_task(coordinator.run("a", effect))
        await asyncio.sleep(0)
        left.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await left
        release.set()
        try:
            result = await right
        except asyncio.CancelledError as error:
            raise AssertionError("shared work cancelled") from error
        require(result == 8 and len(calls) == 1, "waiter cancellation repeated work")


def scheduled(module, case):
    scheduler = module.Scheduler()
    effects = []

    def effect(identifier, payload):
        effects.append((identifier, payload))

    scheduler.schedule("a", 5, "parcel")
    if case == "cancel-before-due":
        require(scheduler.cancel("a") is True, "pending cancellation rejected")
        scheduler.run(5, effect)
        require(
            not effects and scheduler.jobs["a"]["status"] == "cancelled", "cancelled job executed"
        )
    elif case == "due-complete-and-terminal-cancel":
        scheduler.run(4, effect)
        require(not effects, "early delivery")
        scheduler.run(5, effect)
        scheduler.run(50, effect)
        require(effects == [("a", "parcel")], "duplicate completed effect")
        require(
            scheduler.cancel("a") is False and scheduler.jobs["a"]["status"] == "done",
            "late cancel rewrote completion",
        )
    elif case == "retry-budget-and-deadline":
        attempts = []

        def failing(*args):
            attempts.append(1)
            raise ValueError("transient")

        scheduler.run(5, failing)
        scheduler.run(6, failing)
        require(
            len(attempts) == 1 and scheduler.jobs["a"]["status"] == "retry",
            "retry state or deadline wrong",
        )
        scheduler.run(7, failing)
        scheduler.run(9, failing)
        scheduler.run(100, failing)
        require(
            len(attempts) == 3 and scheduler.jobs["a"]["status"] == "failed", "retry budget wrong"
        )
    elif case == "schedule-identity-and-retry-cancel":
        scheduler.schedule("a", 5, "parcel")
        raises(lambda: scheduler.schedule("a", 6, "parcel"))
        raises(lambda: scheduler.schedule("a", 5, "changed"))

        def failing(*args):
            raise ValueError("controlled")

        scheduler.run(5, failing)
        require(scheduler.cancel("a") is True, "retry cancellation rejected")
        scheduler.run(7, effect)
        require(not effects, "retry cancellation ignored")


NETWORK_MODULES = {"urllib", "http", "socket", "ftplib", "smtplib", "telnetlib", "xmlrpc", "ssl"}


def boundary(module, case, source):
    if case == "no-vendor-or-network-dependency":
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                require(
                    all(
                        x.name.split(".")[0] in sys.stdlib_module_names
                        and x.name.split(".")[0] not in NETWORK_MODULES
                        for x in node.names
                    ),
                    "third-party import",
                )
            elif isinstance(node, ast.ImportFrom):
                require(
                    (node.module or "").split(".")[0] in sys.stdlib_module_names
                    and (node.module or "").split(".")[0] not in NETWORK_MODULES,
                    "third-party import",
                )
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                require(
                    node.value.split(".")[0]
                    not in NETWORK_MODULES | {"requests", "vendor_sdk", "httpx"},
                    "dynamic optional vendor lookup remains",
                )
    elif case == "unicode-and-trim-behavior":
        require(
            module.normalize("  Straße  ", True) == {"name": "strasse", "enabled": True},
            "Unicode normalization changed",
        )
        require(
            module.normalize("", False) == {"name": "", "enabled": False},
            "empty valid name changed",
        )
    elif case == "strict-invalid-values":
        for name, enabled in [("ok", "false"), ("ok", 1), (None, True), (3, False), ("ok", None)]:
            raises(lambda n=name, e=enabled: module.normalize(n, e))


def optimization(module, case):
    if case == "typed-values-and-invalid-input":
        for bad in [True, False, 0, 10, "2", None, []]:
            raises(lambda b=bad: module.compute([{"sku": "a", "qty": 1}, {"sku": "a", "qty": b}]))
        raises(lambda: module.compute([{"sku": "", "qty": 1}]))
    elif case == "order-and-distinct-quantities":
        records = [
            {"sku": "a", "qty": 1},
            {"sku": "a", "qty": 2},
            {"sku": "b", "qty": 3},
            {"sku": "a", "qty": 1},
        ]
        original = json.loads(json.dumps(records))
        require(
            module.compute(records) == [("a", 7), ("a", 14), ("b", 21), ("a", 7)],
            "cached value changes order or amount",
        )
        require(records == original, "input mutated")
    elif case == "deterministic-validation-operation-count":
        calls = []
        validate = module.validate

        def tracked(record):
            calls.append(1)
            return validate(record)

        module.validate = tracked
        records = [{"sku": "a", "qty": 2} for _ in range(100)] + [
            {"sku": "b", "qty": 3} for _ in range(100)
        ]
        require(module.compute(records) == [("a", 14)] * 100 + [("b", 21)] * 100, "output changed")
        require(len(calls) == 2, f"expected two validations, observed {len(calls)}")
        return {"validation_calls": len(calls), "records": len(records)}


CASES = {
    "duplicate-work": [
        "same-key-effect-and-cache",
        "different-keys-progress",
        "failed-work-retry",
        "failed-effect-after-waiter-cancel-can-retry",
        "cancelled-waiter-does-not-cancel-shared-effect",
    ],
    "scheduled-delivery": [
        "cancel-before-due",
        "due-complete-and-terminal-cancel",
        "retry-budget-and-deadline",
        "schedule-identity-and-retry-cancel",
    ],
    "module-boundary": [
        "no-vendor-or-network-dependency",
        "unicode-and-trim-behavior",
        "strict-invalid-values",
    ],
    "repeated-validation": [
        "typed-values-and-invalid-input",
        "order-and-distinct-quantities",
        "deterministic-validation-operation-count",
    ],
}


def main():
    task, root = sys.argv[1:]
    source_path = Path(root) / "solution.py"
    source = source_path.read_text()
    results = []
    for case in CASES[task]:
        metrics = None
        try:
            spec = importlib.util.spec_from_file_location("candidate_solution", source_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if task == "duplicate-work":
                asyncio.run(duplicate(module, case))
            elif task == "scheduled-delivery":
                scheduled(module, case)
            elif task == "module-boundary":
                boundary(module, case, source)
            else:
                metrics = optimization(module, case)
            status, detail, exit_code = "passed", "behavior matched", 0
        except AssertionError as error:
            status, detail, exit_code = "assertion_failed", str(error), 1
        except Exception as error:
            status, detail, exit_code = (
                "infrastructure_error",
                type(error).__name__ + ": " + str(error),
                1,
            )
        results.append(
            {
                "name": case,
                "status": status,
                "detail": detail,
                "exit_code": exit_code,
                "metrics": metrics,
            }
        )
    print(json.dumps({"passed": all(x["exit_code"] == 0 for x in results), "checks": results}))


if __name__ == "__main__":
    main()
