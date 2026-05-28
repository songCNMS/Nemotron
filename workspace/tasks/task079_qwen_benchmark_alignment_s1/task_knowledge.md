# task079_qwen_benchmark_alignment_s1 knowledge

<!-- METADATA:SESSION=1 -->

## Working Notes

- Countable Qwen benchmark-improvement evidence must use `/v1/chat/completions`,
  a parser-compatible final-answer contract, adequate max tokens, checked raw
  artifacts, and explicit baseline/current deltas.
- M1 full-basket launcher availability is regression-run scope, not proof that
  parser-sensitive MMLU-Pro/AIME25/HMMT rows are valid improvement evidence.
- M2 eval basket rows are still config-only because live assets, cluster
  runtime, and frozen Qwen3.5-122B-A10B baselines are absent.
- PR #182 and PR #183 are context only for this task; do not rewrite those
  branches or count their sidecar/targeted-smoke records as merged gate evidence.
