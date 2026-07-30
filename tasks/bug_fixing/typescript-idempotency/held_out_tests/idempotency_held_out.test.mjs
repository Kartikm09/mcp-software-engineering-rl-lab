import assert from "node:assert/strict";
import test from "node:test";

import { IdempotencyGate } from "./idempotency.ts";

test("distinct keys retain distinct work", async () => {
  const gate = new IdempotencyGate();
  const [first, second] = await Promise.all([
    gate.run("a", async () => "A"),
    gate.run("b", async () => "B"),
  ]);
  assert.deepEqual([first, second], ["A", "B"]);
});

test("failed work can be retried", async () => {
  const gate = new IdempotencyGate();
  await assert.rejects(gate.run("retry", async () => Promise.reject(new Error("temporary"))));
  assert.equal(await gate.run("retry", async () => "recovered"), "recovered");
});

