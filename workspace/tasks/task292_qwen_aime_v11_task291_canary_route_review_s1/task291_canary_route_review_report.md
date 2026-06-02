# task292 independent review report - task291 canary route

<!-- METADATA:STATUS=Complete,ASSIGNEE=intern_nemotron_worker_4,SESSION=2 -->

## Decision

- Decision: `APPROVE_CANARY_ROUTE_PASS`
- Reviewed PR: #354
  `https://github.com/songCNMS/Nemotron/pull/354`
- Reviewed exact PR head:
  `2fda1ed46da4c82712a5c22c85bf124c26c6376f`
- Evidence source head:
  `dfb6ca64a5479990be9d4f54defb9f294c09866f`
- Artifact root:
  `/work-agents/intern_nemotron_worker_2/outputs/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_20260602T081136Z`
- Mailbox report:
  `2859a46c6db94679ae1ec64177120dee`
- Review PR:
  `https://github.com/songCNMS/Nemotron/pull/355`

This approval is for task291 non-AIME no-export/no-endpoint canary route
evidence only. It does not authorize AIME/task243 eval, export, endpoint,
promotion, 30B, 8-GPU, or any first go/no-go.

## Read-only checks

- `gh pr view 354 --json number,state,baseRefName,headRefName,headRefOid,mergeStateStatus,isDraft,url,title`
- `git diff --name-status origin/main...2fda1ed46da4c82712a5c22c85bf124c26c6376f`
- `git diff --check origin/main...2fda1ed46da4c82712a5c22c85bf124c26c6376f`
- `git diff --name-status dfb6ca64a5479990be9d4f54defb9f294c09866f..2fda1ed46da4c82712a5c22c85bf124c26c6376f`
- `git show` on the task291 report, helper, README, history, and knowledge at
  the reviewed head.
- `sha256sum` on key canary artifacts, manifests, logs, and source/root marker
  files.
- `jq` on `canary_summary.json`, `canary_prompt_manifest.json`,
  `checkpoint_load_manifest.json`, `command_env_manifest.json`, and
  `canary_results.jsonl`.
- Recomputed every file listed in `checksum_manifest.json`; all matched.
- Tailed `remote_no_export_canary_probe.log`.

No canary run, training, AIME/task243 eval, export, endpoint launch, promotion,
task255 reuse, shared deletion, 30B, or 8-GPU action was performed.

## PR scope

PR #354 was observed OPEN/base `main`/CLEAN/MERGEABLE at
`2fda1ed46da4c82712a5c22c85bf124c26c6376f`.

The diff from `origin/main` contains worker_2 status plus task291 docs/report
and task-owned helper:

- `workspace/interns/intern_nemotron_worker_2/status.md`
- `workspace/tasks/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/README.md`
- `workspace/tasks/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/history_log.md`
- `workspace/tasks/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/no_export_canary_route_unblock_report.md`
- `workspace/tasks/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_no_export_canary_probe.py`
- `workspace/tasks/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/task_knowledge.md`

`git diff --check` was clean. The drift from the evidence source head
`dfb6ca64` to PR head `2fda1ed` added official report/closeout metadata and did
not invalidate the artifact source head.

## Artifact verdict

Local markers:

- `source_head.txt`:
  `dfb6ca64a5479990be9d4f54defb9f294c09866f`
- `remote_run_root.txt`:
  `/root/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_20260602T081136Z`
- `remote_no_export_canary_probe.rc`: `0`

Verified sha256 values:

| File | sha256 |
|---|---|
| `artifacts/canary/canary_summary.json` | `dd855c2c32b0b7411ee1cd365311363f1d3338753560107768b684b8fb660d40` |
| `artifacts/canary/canary_decision.json` | `c3c9964b6024e1fb137c0db66d255e773727dc8d30fde75c56834b34778c0bca` |
| `artifacts/canary/canary_results.jsonl` | `67e6304786f5bb79fee07f5253ff4de2e449d2756aa6fd2d38762322bdad3dc7` |
| `artifacts/canary/canary_full_completions.jsonl` | `b2768f75415abfeb268b58ba425abe41a7b169fdacbd07e9aa27422e46d7611d` |
| `artifacts/manifests/canary_prompt_manifest.json` | `87993e038420a850723551f0a5118068e734c41130f8f316d8b814a714f61e73` |
| `artifacts/manifests/checkpoint_load_manifest.json` | `f3c974552ae182ab93ec122f6038650fc57479133034d2971b1c277dad8f4390` |
| `artifacts/manifests/command_env_manifest.json` | `24edd402c7772931a2d6422865b16baa7ec2dae9fe9881bc5a5742fd72ccee76` |
| `artifacts/manifests/checksum_manifest.json` | `08477bf8be669314a54359edeeca16de4605262ce5d553944e3477e4ff46f97d` |
| `logs/remote_no_export_canary_probe.log` | `e2044aae855a7a660968e3d2940c946ca874198bef2a04e05163c4235707f17b` |
| `logs/remote_no_export_canary_probe_command.txt` | `09f53671a35a05c4c9f158f28faa63fee7b2ae9eff57bc51cbdb935dadc462b5` |
| `logs/sync_to_nemtron.log` | `9193ea64e5774f6d85010761c68697777f60ee156f370eaf964218b08b895486` |

## Metrics and provenance

`canary_summary.json` reports:

- `disposition`: `PASS`
- `canary_pass`: `true`
- route:
  `direct_in_process_mcore_static_engine_no_export_no_endpoint_topk1_greedy`
- prompts requested: `5`
- completions retained: `5`
- exact expected-answer matches: `5`
- final-answer marker count: `9`
- prompt YAML sha:
  `150ee11dc6e8efd3c865a8e9ed8a9ab8ce4f5ee032bed383c73a6cea34f52f1c`

`canary_results.jsonl` has five rows. Extracted answers matched expected values:
`95`, `15`, `29`, `247`, and `go`.

`canary_prompt_manifest.json` confirms the prompt set is synthetic, non-AIME,
excludes AIME2025, excludes training rows, and has no AIME2025 prompt or label
text.

`checkpoint_load_manifest.json` confirms `load_megatron_model: PASS` for the
task285 iter2 checkpoint on `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`,
with model device `cuda:0`, dtype `torch.bfloat16`, eval mode, Qwen3-style 36
layers, hidden size 2560, and sequence length 4096.

`command_env_manifest.json` confirms `CUDA_VISIBLE_DEVICES=0`, one visible H200,
and boundary confirmations for Qwen3-4B only, no training/optimizer, no
AIME/task243, no AIME2025 train prompts/labels, no task255, no export or
conversion, no endpoint, no promotion, no shared deletion, no 30B, and no
8-GPU.

## Residual risks

- `synthetic_word_completion_ready_set` used
  `generated_tokens_detokenize_fallback` because MCore `generated_text` was
  empty while generated token ids decoded to retained text. This is acceptable
  for the narrow route-pass evidence but should remain visible in downstream
  gate notes.
- This is a five-prompt synthetic non-AIME route proof only. It is not an
  AIME/task243 same-harness comparison, not export/endpoint proof, not
  promotion evidence, and not 30B/8-GPU clearance.
