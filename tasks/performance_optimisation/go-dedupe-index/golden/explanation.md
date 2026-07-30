# Golden Explanation

The nested scan made worst-case work quadratic in the number of unique values. A local set provides one membership check per input while appending only on the first occurrence, so order remains stable. Expected work becomes O(n) time with O(n) additional space. The deterministic check count is the CI threshold; benchmark timing is recorded but remains machine-dependent.

