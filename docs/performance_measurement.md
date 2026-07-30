# Performance Measurement

The Go task demonstrates a stable approach to optimization evaluation.

## Acceptance strategy

1. A deterministic operation counter must be no greater than input length.
2. Output must preserve first-occurrence order.
3. Public and held-out functional tests must pass.
4. `go test -run '^$' -bench BenchmarkUnique -benchtime=100x` records supporting wall-clock evidence.

The deterministic counter is the gate because shared CI timing is noisy. Benchmark output is retained to show the real command ran, but the repository does not advertise a speedup percentage from one machine.

## Extending the method

For larger tasks, record warm-up runs, at least five measured samples, median and dispersion, fixed fixtures, toolchain versions, and a noise-tolerant threshold. Reject a performance patch if correctness or output ordering changes, regardless of measured speed.
