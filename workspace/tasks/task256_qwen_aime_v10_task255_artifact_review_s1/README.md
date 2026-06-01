# task256_qwen_aime_v10_task255_artifact_review_s1 - task255 artifact review

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_5,SESSION=2 -->

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

## Session 2 Review Closeout

- Recommendation: REQUEST_CHANGES / HOLD before task243 or task257 uses the
  task255 HF export as the candidate FT artifact.
- Reason: the task255 report and worker_2 logs are internally consistent, but
  the exact requested checkpoint and HF export directories under
  `/root/task255_qwen_aime_v10_qwen4b_pilot_checkpoint_s1/run_20260601T202339Z`
  are not present/readable from worker_5's review environment. Direct
  `test -d` / `find` checks returned `MISSING_OR_UNREADABLE`, and
  `find /root -maxdepth 5 -path '*task255*' -print` found no local task255
  artifact copy.
- PR freshness: `gh pr view 329` reported PR #329 OPEN/CLEAN, base `main`, head
  `d62036e405edc5daa322c09bb89da19b176bb7bf`. Diff from
  `dfee98a028a55c00dc2579bef602ee914e88a325` to PR #329 changed only
  `workspace/interns/intern_nemotron_worker_2/status.md`.
- Report integrity: report sha256 matched the expected
  `3893af84bfdb4d78c4f31074a8454b2fa2bab2d69cfec71c42a36b75c49e7686`.
- Log-backed checkpoint evidence: `checkpoint_inventory_20260601T202339Z.log`
  reports `latest_checkpointed_iteration.txt` at `1`, 18 files, 53G, and large
  distcp shard hashes
  `383f015cc80591e8309409a9e1416c6bfe93bb7ddcc7f124dcdccb3c3429bbf6`,
  `d14a43bb54a056c3a8ddadf7b5766e0aea09adbcef3c49dbbe1333107c86e6b2`,
  `e64e4f1dfe66e1ad08777ef8239ea598b7c4a3ce27c3e0c745a87a7e5e50bb11`,
  and `8c4c7ebaf1a52b146400cccfe283c4a5d592a803ed3c549af47a6ec08fa9d5c9`.
- Log-backed HF export evidence: `hf_export_inventory_20260601T202339Z.log`
  reports 13 files, 7.6G, three safetensor shards, and `config.json` hash
  `74e923dd507a5ecec8d596353290ca705ef8e4b7191d5823bbd4b77040515012`.
  Safetensor hashes are
  `83117ed49e8e3b56e07f0f328bcf9c021ee517d30e58dcb57dbfb1f8480b4474`,
  `2194bbacbcfff92ef6da346a0f58f3d5a5c0bac63356ae7604cb0240290032f2`,
  and `b4828ee7fab6b139df83bf7da36af828d08957deb97a8851e8c02155892980ec`.
- Export/train logs: `train_retry_no_training_contract_cli_20260601T202339Z.log`
  ends with one iteration, checkpoint save, packed-valid validation, and
  `COMMAND_RC=0`; `export_hf_20260601T202339Z.log` reports
  `Success: All tensors from the original checkpoint were written.` and
  `EXPORT_COMMAND_RC=0`.
- Input checksums: `remote_input_checksums_20260601T202339Z.log` matches the
  task253 metadata, blend, and shard-summary hashes listed in Suggested Checks;
  `remote_qwen_contract_20260601T202339Z.log` reports `QWEN_CONTRACT_OK`.
- Config evidence: the base model path is readable and has Qwen3 4B-class
  metadata (`Qwen3ForCausalLM`, `model_type=qwen3`, 36 layers, hidden size 2560,
  32 attention heads, 8 KV heads, intermediate size 9728, vocab size 151936).
  The exported `config.json` contents could not be independently read from the
  inaccessible HF export directory.
- Boundary assessment: no training rerun, export rerun, AIME/task243 eval,
  promotion claim, 30B/8-GPU launch, shared artifact deletion, or code edit was
  performed by worker_5. The task255 logs/report indicate task255 used
  `CUDA_VISIBLE_DEVICES=0,1`, `--nproc_per_node=2`, packed-valid validation
  only, and no `/mnt/cephfs/data/processing/lei.song` deletion.
- Required change: expose the exact checkpoint/HF export artifacts to reviewers,
  or provide a lead-accepted copied artifact bundle/manifest whose file hashes
  can be independently verified, before any task243 same-harness comparison
  consumes this FT export.

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
