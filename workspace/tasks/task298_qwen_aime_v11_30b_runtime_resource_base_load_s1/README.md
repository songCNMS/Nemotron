# task298_qwen_aime_v11_30b_runtime_resource_base_load_s1 - 30B runtime/resource/base-load gate

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_2,SESSION=76 -->

## Background

The user requested a full 30B Qwen AIME V11 data -> training -> testing run
from current main `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7`. The accepted 4B
current-main equivalence gate is complete, but 30B scale must start with a
fail-closed runtime/resource/base-load proof before any 30B training or testing.

Candidate model path from coordinator:
`/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`. Nearby
variants include `Qwen3-30B-A3B-Base`, `Thinking`, and `FP8`; do not substitute
without reporting why.

## Goal

Prove or block the launch route for 30B Qwen AIME V11 by identifying the exact
model path, GPUs/resources, parallelism, bridge/import/load path, training
entrypoint, eval/testing route, and whether any eval-only export/endpoint is
required.

## Scope

- Sync current code to NemTron `/root` before any remote debug, per project
  rule.
- Inspect the candidate 30B path and nearby Qwen paths read-only.
- Run no-training base-load/import/config preflight only.
- Identify required GPU count/type, tensor/pipeline/expert parallelism, memory
  constraints, and launcher entrypoint for the later full SFT task.
- Identify whether corrected AIME testing can run no-export, or whether an
  eval-only export/endpoint is required. Eval-only export/endpoint is allowed
  only as a route finding result, not promotion.

## Boundaries

- Do not train, run optimizer steps, run corrected AIME scoring, run non-AIME
  canary, export for promotion, launch a production endpoint, promote, reuse
  task255, use AIME2025 prompts/labels as train data, delete shared files under
  `/mnt/cephfs/data/processing/lei.song`, push main, merge, or mutate shared
  model/data roots.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_2/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1`
- Report:
  `workspace/tasks/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/30b_runtime_resource_base_load_report.md`
- Artifact root under worker outputs with command logs, environment capture,
  remote run path, model-path inventory, config/preflight output, and checksums.
- Mailbox report with branch/head/PR, exact commands/env, exact model path,
  GPU/resource recommendation, parallelism proposal, training entrypoint,
  eval-route/export-route decision, pass/fail disposition, artifacts, and
  blockers.

## Acceptance Criteria

- PASS: Qwen3-30B-A3B path and runtime route are proven enough to allow later
  no-AIME data/packing, base testing, and training tasks to proceed under
  documented resources and fail-closed commands.
- REQUEST-CHANGES: report is missing commands, model path proof, resource
  details, entrypoint, or eval-route decision.
- BLOCK: model path is unavailable/unloadable, runtime lacks resources or
  dependencies, or required export/endpoint/training route cannot be bounded
  safely.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Current main: `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7`
- Related tasks: task276, task285, task293, task296, task297
