# task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1 - Qwen3-4B pilot checkpoint

<!-- METADATA:STATUS=ReadyForReview,ASSIGNEE=intern_nemotron_worker_2,SESSION=3 -->

## Closeout

worker_2 reported `PASS_ARTIFACT_READY_FOR_REVIEW` at PR #329 head
`d62036e405edc5daa322c09bb89da19b176bb7bf`. The artifact is ready for
independent review and same-harness AIME planning, but task255 makes no quality,
promotion, task243 comparison, or go/no-go claim.

## Lead Gate Update

#329 remains `HOLD`, not approved. task256 request-changed independent artifact
review because the `/root/task255_...` checkpoint/export paths were not
reviewer-accessible to worker_5. task257 PR #330 records a same-harness FT
AIME25 result of `0/30 = 0.0`, below the accepted base `11/30`, so the current
candidate is not promotable even if artifact access is later resolved.

#329 was later closed unmerged as superseded by #331. #331 merged the task255
artifact-record docs plus task258 reviewer-access closeout. The candidate
remains a failed/no-promotion record.

## Background

task253 produced Qwen3-4B V10 local `packed_qwen` shards, and task254
independently approved them as local prep evidence only. The global Qwen AIME
gate still lacks a candidate fine-tuned Qwen3-4B checkpoint/export artifact and
the task243 same-harness FT-vs-base comparison.

Accepted base score for the same-harness corrected AIME2025 protocol remains
`11/30 = 0.36666666666666664` for
`/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.

## Goal

Produce a bounded Qwen3-4B V10 pilot training/checkpoint/export artifact from
the reviewed task253 packed shards, or report the exact resource/environment
blocker that prevents producing the candidate FT artifacts.

## Scope

- Start from current `origin/main` after #328 merge commit
  `61fa65e9e9a535d531a65072c839760c3488207f`.
- Use Qwen3-4B only:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Use reviewed task253 packed shards:
  `/work-agents/intern_nemotron_worker_2/outputs/task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1/packed_qwen/splits`.
- Preserve Qwen tokenizer-native chat template settings:
  `enable_thinking=false` and `truncate_history_thinking=false`.
- If running on remote node `NemTron`, sync code to `/root` before debug or
  training, and record the exact sync path.
- Keep the pilot bounded and cheap: Qwen3-4B only, no 30B, no 8-GPU scale, and
  stop after a short smoke/pilot sufficient to produce checkpoint/export
  evidence or a precise blocker.

## Boundaries

- Do not train on AIME2025 prompts or labels; AIME2025 remains held-out
  eval/decontam only.
- Do not run task243 same-harness comparison; task243/worker_3 will own that
  after candidate FT artifacts exist.
- Do not run FT live eval as part of this task unless lead explicitly creates a
  separate eval task.
- Do not claim promotion, go/no-go pass, or 30B/8-GPU clearance.
- Do not delete or overwrite existing files under
  `/mnt/cephfs/data/processing/lei.song`.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_2/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1`.
- PR only if repo docs/config/scripts must change; artifact-only closeout is
  acceptable if no repo change is needed.
- Task-owned output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1/`.
- Report with:
  - branch/head/PR or artifact-only status;
  - exact commands, environment, host, GPU/resource shape, and code sync path;
  - input packed shard manifest/checksums;
  - training config and step/iteration bounds;
  - checkpoint/export paths, counts, and checksums if produced;
  - logs and failure diagnosis if blocked;
  - confirmation no AIME2025 prompts/labels were trainable data;
  - explicit statement that no task243 comparison, promotion, or 30B/8-GPU was
    run.
- Mailbox report to `intern_nemotron_lead`.

## Acceptance Criteria

- PASS: a candidate Qwen3-4B pilot checkpoint/export artifact exists with
  reproducible commands, logs, paths, checksums, and boundary confirmation.
- BLOCKED: no checkpoint/export exists, but the blocker is precise and
  reproducible with commands, logs, resource state, and remediation path.
- The global gate remains `NO-GO/HOLD` until task243 proves same-harness
  `ft_exact_normalized_accuracy >= 11/30` against the accepted base protocol.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Depends on: task253, task254, task246, task247, task248
- First gate: candidate Qwen3-4B pilot checkpoint/export artifact or exact
  blocker; no eval/promotion/30B.
