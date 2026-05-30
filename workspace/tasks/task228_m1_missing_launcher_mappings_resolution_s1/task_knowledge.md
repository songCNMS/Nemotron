# Task Knowledge

<!-- METADATA:SESSION=1 -->

- `m1_eval_launcher_mapping.yaml` intentionally separates the intended M1
  benchmark registry from concrete `nemo-evaluator-launcher` task names.
  Rows with `status=missing` must not be replaced with related-but-different
  benchmarks.
- The task225 runtime package reports `nemo-evaluator-launcher==0.2.5` with
  421 packaged task IRs.
- The task225 package resource hashes observed for task228 are:
  - `all_tasks_irs.yaml`:
    `b0e56d00ffddebd60a81cef654e6e037b38f5ed72dc985ded3e94b237649e394`
  - `mapping.toml`:
    `684a594af1f5dbd089d2eb04366579a6ecd43a02cdd09770006badc1aa2325d7`
- `terminalbench` resolves to `codec.terminalbench` in the package, but that
  task is described as contamination detection, not TerminalBench benchmark
  evaluation.
- `codec.swebench_test` and `codec.swebench_train` are SWE-bench
  contamination-detection tasks, not SWE-Bench Verified evaluation.
- No `mcp_mark` task/key appears in the package task mapping.
- ToolTalk and BFCL are tool-use tasks but are not safe replacements for
  Tool-Decathlon without benchmark-owner confirmation and an exact scoring
  contract.
