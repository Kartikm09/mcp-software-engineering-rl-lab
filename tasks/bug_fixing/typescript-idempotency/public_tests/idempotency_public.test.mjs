import assert from "node:assert/strict";
import test from "node:test";

import { IdempotencyGate } from "./idempotency.ts";

test("same-key calls share one operation", async () => {
  const gate = new IdempotencyGate();
  let calls = 0;
  const operation = async () => {
    calls += 1;
    await new Promise((resolve) => setTimeout(resolve, 10));
    return "value";
  };
  const results = await Promise.all([gate.run("same", operation), gate.run("same", operation)]);
  assert.deepEqual(results, ["value", "value"]);
  assert.equal(calls, 1);
});

