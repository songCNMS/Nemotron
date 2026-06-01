# task256_qwen_aime_v10_task255_artifact_review_s1 - task255 artifact review

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_5,SESSION=0 -->

## Background

task255 produced a bounded Qwen3-4B V10 one-iteration pilot artifact from the
reviewed task253 packed shards. worker_2's current artifact PR is #329 at
`d62036e405edc5daa322c09bb89da19b176bb7bf`. The previous artifact closeout
head `dfee98a028a55c00dc2579bef602ee914e88a325` differs from `d62036e` only by
worker status PR-number bookkeeping.

The global Qwen AIME gate remains `NO-GO/HOLD`: task255 artifacts are not a
quality result, promotion claim, or same-harness AIME comparison.

## Goal

Independently review the task255 checkpoint/export artifacts and report
approve/request-changes/block for using the HF export as the candidate FT model
in the corrected AIME2025 same-harness comparison.

## Scope

- Review task255 PR #329 head:
  `d62036e405edc5daa322c09bb89da19b176bb7bf`.
- Review task255 report:
  `/work-agents/intern_nemotron_worker_2/outputs/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1/task255_qwen4b_pilot_checkpoint_export_report.md`.
- Review checkpoint artifact:
  `/root/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1/run_20260601T202339Z/checkpoints_retry_no_training_contract_cli`.
- Review HF export artifact:
  `/root/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1/run_20260601T202339Z/hf_export_iter_0000001`.
- Review local logs:
  `/work-agents/intern_nemotron_worker_2/outputs/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1/logs/`.

## Suggested Checks

- Verify the worker report sha256:
  `3893af84bfdb4d78c4f31074a8454b2fa2bab2d69cfec71c42a36b75c49e7686`.
- Verify checkpoint inventory, HF export inventory, file counts, sizes, and
  checksums against worker_2's report.
- Verify the HF export has Qwen3 config/tokenizer files and three safetensors
  shards:
  - `model-00001-of-00003.safetensors`;
  - `model-00002-of-00003.safetensors`;
  - `model-00003-of-00003.safetensors`.
- Verify the export config is Qwen3/Qwen3ForCausalLM and points to a 4B-class
  architecture.
- Verify input checksums match the reviewed task253 packed metadata:
  - metadata sha256
    `18a83f43bdecaed886bd115945e3b767c99479bf6dafae20be544e21b36afac3`;
  - blend sha256
    `963ad31c2265eaf9f10fdd261eb73705e72b83fbc0fff2b00f49891bfcbb0520`;
  - shard summary sha256
    `03d1e72da96c6c10528f8a218cca3e20b461268daae35b4388d566249705f040`.
- Verify report/boundary claims: no AIME2025 train prompts/labels, no task243
  comparison, no FT live eval beyond packed-valid training validation, no
  promotion/go-no-go claim, no 30B/8-GPU, and no shared `lei.song` deletion.

Run only read-only or lightweight integrity checks. Do not run AIME eval,
training, promotion checks, or destructive commands.

## Boundaries

- Do not edit code, commit product changes, push main, merge, or self-merge.
- Do not modify or delete worker_2 artifacts.
- Do not train, export again, run AIME/task243 comparison, run FT live eval,
  claim promotion, or launch 30B/8-GPU.
- Do not delete or overwrite anything under `/mnt/cephfs/data/processing/lei.song`.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_5/task256_qwen_aime_v10_task255_artifact_review_s1`.
- PR only if docs/status changes need review; artifact-only/mailbox closeout is
  acceptable if no repo changes are needed.
- Mailbox report to `intern_nemotron_lead` with:
  - exact branch/head and artifact paths reviewed;
  - commands/checks run and pass/fail results;
  - checksum/count/metadata mismatches if any;
  - boundary assessment;
  - approve/request-changes/block recommendation;
  - residual risks for task257/task243 comparison.

## Acceptance Criteria

- APPROVE means the task255 HF export can be used as the candidate FT artifact
  for the corrected AIME2025 same-harness comparison.
- REQUEST-CHANGES means worker_2 must fix/report missing artifact evidence
  before task243 comparison proceeds.
- BLOCK means artifact integrity or boundary evidence is insufficient for
  comparison.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_5`
- Related task: `task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1`
- First gate: artifact integrity and boundary review only.
