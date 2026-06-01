# task254_qwen_aime_v10_task253_packing_artifact_review_s1 - task253 packing artifact review

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_5,SESSION=1 -->

## Background

task253 produced an artifact-only closeout for Qwen3-4B V10 local packing after
task251/#328 unblocked HotpotQA. worker_2 reports
`PASS_PACKED_QWEN_LOCAL_ONLY` at branch head
`749ade2e05b18ae0f1083342eeef0f8a2d61b11e`, with no PR because no repo
code/config/script changes were needed.

The global Qwen AIME gate remains `NO-GO/HOLD`: packed shards are local prep
evidence only, not a candidate FT checkpoint/export/live eval artifact.

## Goal

Independently review and, where useful, lightly verify the task253 local packed
Qwen artifact evidence so lead can decide approve/request-changes/block for the
local packing precondition.

## Scope

- Review exact task253 branch head:
  `749ade2e05b18ae0f1083342eeef0f8a2d61b11e`.
- Review worker_2 report:
  `/work-agents/intern_nemotron_worker_2/outputs/task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1/qwen_packing_xenna_unblock_report.md`.
- Review artifact paths:
  - packed root:
    `/work-agents/intern_nemotron_worker_2/outputs/task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1/packed_qwen`;
  - split root:
    `/work-agents/intern_nemotron_worker_2/outputs/task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1/packed_qwen/splits`;
  - shard summary:
    `/work-agents/intern_nemotron_worker_2/outputs/task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1/packed_qwen_shard_summary.json`.
- Verify report consistency for:
  - commands/environment;
  - `cosmos_xenna` and `pydantic_settings` import probes;
  - Qwen3-4B tokenizer path
    `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`;
  - `chat_template=tokenizer`;
  - `enable_thinking=false`;
  - `truncate_history_thinking=false`;
  - metadata and blend checksums;
  - shard counts/checksums and train/valid split summary;
  - no AIME2025 train prompts/labels added by task253;
  - no NemTron training, FT eval, task243 comparison, promotion claim, or
    30B/8-GPU.

## Suggested Checks

Run only lightweight read-only checks. Examples:

```bash
sha256sum \
  /work-agents/intern_nemotron_worker_2/outputs/task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1/packed_qwen/splits/metadata.json \
  /work-agents/intern_nemotron_worker_2/outputs/task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1/packed_qwen/blend.json
```

```bash
python -m json.tool \
  /work-agents/intern_nemotron_worker_2/outputs/task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1/packed_qwen_shard_summary.json >/tmp/task254_shard_summary.json
```

Optional, if the environment supports it without modifying artifacts:

```bash
PYTHONPATH=src python - <<'PY'
from pathlib import Path
from nemotron.recipes.super3.stage1_sft.qwen_chat_contract import validate_qwen_packed_sft_chat_contract
validate_qwen_packed_sft_chat_contract(
    Path('/work-agents/intern_nemotron_worker_2/outputs/task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1/packed_qwen/splits'),
    tokenizer_model='/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507',
)
print('qwen_chat_contract PASS')
PY
```

If any check cannot run, report the exact environment blocker rather than
editing code or artifacts.

## Boundaries

- Do not edit code, commit, push, open PRs, merge, or rewrite worker_2's branch.
- Do not modify or delete task253 outputs.
- Do not train, sync to NemTron for training, run FT live eval, run task243
  comparison, claim promotion, or launch 30B/8-GPU.
- Do not delete or overwrite anything under `/mnt/cephfs/data/processing/lei.song`.
- Do not treat packed shards as candidate FT checkpoint/export/live eval
  artifacts.

## Expected Output

- Mailbox report to `intern_nemotron_lead` with:
  - exact branch/head and artifact paths reviewed;
  - commands/checks run and pass/fail results;
  - any checksum/count/metadata mismatches;
  - contamination/boundary assessment;
  - approve/request-changes/block recommendation;
  - residual risk, especially around user-site pip dependency conflicts.

## Acceptance Criteria

- The review explicitly covers task253 head
  `749ade2e05b18ae0f1083342eeef0f8a2d61b11e`.
- The review either confirms the reported packed shards are reproducible enough
  for local prep evidence, or identifies exact missing/mismatched evidence.
- The review preserves the global `NO-GO/HOLD`: no FT promotion or 30B scale
  without task248 candidate artifacts and task243 same-harness FT-vs-base
  comparison against the accepted 11/30 base.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_5`
- Related task: `task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1`
- First gate: independent artifact/repro review only.
