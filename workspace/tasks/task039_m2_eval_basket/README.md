# task039_m2_eval_basket

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Goal

Build the M2 eval basket Session 1 sandbox scaffold: a benchmark
registry plus adapter-config metadata for the M2 acceptance basket.

## Session 1 Scope

- Declare HLE, BrowseComp, BIRD real execution, BFCL full, MCP-Mark,
  Tool Decathlon, multilingual IF, and multilingual code benchmark rows.
- Keep every row sandbox-runnable as configuration validation only.
- Surface cluster/runtime/data/API/Qwen-baseline blockers explicitly per
  benchmark.
- Reuse the existing `eval_basket_registry` schema kind and unified data
  registry validation.

## Out Of Scope

- Live benchmark asset downloads or API calls.
- Full cluster launchers or NeMo Evaluator runs.
- task019 Session 2-3 and task020 Session 3 cluster eval runs.
- Frozen Qwen3.5-122B-A10B baseline numbers and promotion-gate baseline swap.
- W&B publication of final M2 eval results.

## Acceptance

- Focused pytest covers registry loading, adapter metadata validation,
  category grouping, planned benchmark coverage, and deferred-runtime
  blocker reporting.
- Unified registry validation remains clean if the M2 registry is added
  to `unified_index.yaml`.
- New Python modules compile and `git diff --check` passes.
