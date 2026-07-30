# Golden Explanation

The feature derives remaining capacity from the immutable maximum and validates impossible current states. The existing acceptance predicate used a strict comparison, incorrectly rejecting a request that exactly filled the batch; changing it to `<=` matches the discovered contract. All operations remain O(1), allocation-free, and thread-safe.

