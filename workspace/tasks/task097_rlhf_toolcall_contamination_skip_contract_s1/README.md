# task097_rlhf_toolcall_contamination_skip_contract_s1 - RLHF tool-call contamination skip contract

<!-- METADATA:STATUS=InReview,ASSIGNEE=intern_nem_dev_3 -->

## Background

`scripts/prepare_rlhf_toolcall_pairing.py` accepted omitted eval prompts and
silently used an empty contamination set. The paired RLHF tool-call source is
active in the RLHF registry and claims contamination coverage against BFCL,
TauBench airline, MCP-Mark, and HelpSteer1, so accidental eval-prompt omission
must not look like a normal clean run.

## Goals

- Require explicit `--skip-contamination-check` when `--eval-prompts-jsonl` is
  omitted.
- Fail before writing outputs if eval prompts are omitted without the skip flag.
- Keep sandbox/smoke runs possible with the explicit skip flag.
- Record the skip in `manifest.json` with an explicit boolean and warning.
- Preserve output row schema, env id `rlhf_toolcall_paired`, pairing heuristics,
  and active registry status.

## Out Of Scope

- Live HelpSteer/Hermes data prep, production eval-prompt corpus construction,
  endpoint calls, W&B, cluster jobs, deployment, promotion, direct `main` or
  `master` pushes, and self-merge.

## Acceptance

- Focused RLHF tool-call pairing CLI/converter pytest passes.
- `python -m py_compile` passes for the touched CLI and tests.
- Ruff passes for the touched CLI and tests.
- Static probe confirms no live data-prep/download/endpoint/W&B/cluster/deploy
  surface was added.
- `git diff --check` and `git diff --cached --check` pass.

## PR

- https://github.com/songCNMS/Nemotron/pull/203
