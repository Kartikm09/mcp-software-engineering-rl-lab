# Golden Explanation

The implementation treated the one-based attempt number as a zero-based exponent, so attempt 1 used `base * 2`. Subtracting one preserves exponential growth and the existing cap while keeping validation and the public API unchanged. The patch changes one expression and has constant time and space complexity.

