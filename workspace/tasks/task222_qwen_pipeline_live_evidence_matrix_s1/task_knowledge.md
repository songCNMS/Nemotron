# Task Knowledge

<!-- METADATA:SESSION=1 -->

- Task222 must not run GPU, endpoint, train, eval, or benchmark operations.
- Use existing logs/reports only; record artifact paths and exact commands
  where already captured by prior tasks.
- Current verified Qwen pipeline evidence before task220/task221:
  task208 full packing PASS, task210 endpoint/direct math smoke PASS,
  task218 contained causal-conv1d dependency stack PASS, and task219
  canonical single-GPU one-iteration SFT PASS.
- Namespace caveat is central: task208 CPU-created packed artifacts required
  explicit staging for NemTron consumers; task210 staged model is NemTron
  visible but not local CPU visible; task219 checkpoint was verified on NemTron
  while local CPU visibility was missing.
- Remaining pipeline proof requires task220 8-H200 full-data one-iteration SFT
  and task221 full benchmark readiness/run after PM release; current task220
  logs only prove staging, and current task221 logs only prove prepare-state
  visibility/launcher readiness.
