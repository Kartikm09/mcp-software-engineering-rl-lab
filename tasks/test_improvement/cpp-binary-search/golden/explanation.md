# Golden Explanation

The baseline mixed an inclusive upper bound with lower-bound updates, which can skip a candidate and underflow when moving left. A half-open `[low, high)` interval keeps every update valid, naturally supports empty input, and verifies equality before returning the insertion position. Complexity remains O(log n) time and O(1) space.

