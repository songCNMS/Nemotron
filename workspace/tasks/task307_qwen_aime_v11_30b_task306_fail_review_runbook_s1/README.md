# task307_qwen_aime_v11_30b_task306_fail_review_runbook_s1 - 30B task306 fail review and runbook closeout

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_4,SESSION=203 -->

## Background

Task306 returned final corrected AIME2025 artifacts for the task301 Qwen3-30B-
A3B salvage checkpoint `iter_0000035`.

Current lead-observed state:

- `origin/main`: `7a93a6cea16e45284a58287b91c0069b7416fa99`.
- task306 worker branch:
  `intern_nemotron_worker_3/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1`.
- task306 source head:
  `894e2e71e72f09926128e37f22000802804522bc`.
- task306 PR #369 later appeared after the initial task307 assignment and is
  currently OPEN, base `main`, CLEAN, non-draft, head
  `8201b3943db2d6ed4427c42518736c41f77d67bd`.
- The task306 eval source head remains `894e2e71e72f09926128e37f22000802804522bc`;
  PR #369 first reached `1255f2356cb014cd1adbe58c7af297f291b222f3`, then
  advanced to `8201b3943db2d6ed4427c42518736c41f77d67bd` with worker_3
  session/status/PR metadata closeout. Worker_3 official mailbox reports are
  `ae6fd1db7a894003a952469e4705ab07` and addendum
  `094b16ec7ba14650b53bcd9e69306256`.
- task306 local output root:
  `/work-agents/intern_nemotron_worker_3/outputs/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_20260602T190432Z`.
- task306 remote run root:
  `/root/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_20260602T190432Z`.
- Remote/local `remote_no_export_aime_eval.rc` is `0`.
- Corrected AIME summary disposition is `FAIL`: FT `14/30 = 0.4666666666666667`
  versus accepted 30B base `15/30 = 0.5`, delta `-1`.
- FT parser/completion metrics: `30` requested rows, `30` successful responses,
  `17` parsed rows, `14` correct rows, `13` length stops, `17` stop finishes.
- Summary reports prompt-token match with task300 base, same row count/
  denominator, same parser/normalizer, same AIME score cache, and boundary
  confirmations for no AIME2025 train prompts/labels, no task255 reuse, no
  training, no export/conversion, no endpoint, no promotion, no shared deletion,
  no main push/merge.
- Residual to review explicitly: task306 records `sampling_exact_parameter_match`
  as `false` while also recording semantic deterministic greedy match
  (`task300` base used SGLang `temperature=0/top_p=1e-5`; task306 FT used
  MCore in-process `top_k=1`, `temperature=1`, `top_p=0`).

Key artifact hashes observed by lead:

- `artifacts/aime_eval/summary.json`:
  `a3e046e3d5417095bd2d1072609dcdaf90ad17620015062efaac561e028ab947`.
- `artifacts/aime_eval/results.jsonl`:
  `46a702b31208661633b6b783e48f8fac3d6b60e06da3fdb9c3972a51cfa3f827`.
- `artifacts/aime_eval/full_completions.jsonl`:
  `32bb1e75f653711961b052a1008e53c668eb3787b8c5e3ea1369ed7ba8373704`.
- `artifacts/aime_eval/parser_diagnostics.jsonl`:
  `7c185fca5dc94105ff77aca48e70cfdeef8d5560a7b790682bdc312b2e807354`.
- `artifacts/manifests/checksum_manifest.json`:
  `a82f55bc0d9de7adb28aa28812a5d9b8d557a580ac6709cd7483452e3a8f02cd`.

## Goal

Independently review the task306 final artifacts and produce a runbook/
provenance closeout for the 30B Qwen AIME V11 scale-up gate.

The expected lead disposition is no-promotion FAIL if the evidence is
internally consistent: task301 FT `14/30` is below accepted 30B base `15/30`.
If protocol or artifact evidence is incomplete or inconsistent, return HOLD or
request changes instead.

## Scope

- Review exact PR #369 head
  `8201b3943db2d6ed4427c42518736c41f77d67bd`.
- Confirm the task306 eval source head
  `894e2e71e72f09926128e37f22000802804522bc`.
- Compare `894e2e71e72f09926128e37f22000802804522bc..1255f2356cb014cd1adbe58c7af297f291b222f3`
  and state whether it is only worker_3 official report/status/task-doc
  closeout for the completed run.
- Compare `1255f2356cb014cd1adbe58c7af297f291b222f3..8201b3943db2d6ed4427c42518736c41f77d67bd`
  and state whether it is only worker_3 session/status/PR metadata closeout
  with unchanged task306 metrics.
- Confirm whether task306 branch/PR/head changed after this assignment.
- Review the task306 local output root and remote root read-only.
- Verify `remote_no_export_aime_eval.rc=0`.
- Verify artifact presence, line counts, checksums, and checksum manifest
  consistency for summary, results, full completions, parser diagnostics,
  prompt manifest, command/env manifests, checkpoint-load manifests, and rank
  event logs.
- Verify summary fields:
  - model path `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`;
  - checkpoint
    `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints/iter_0000035`;
  - route `direct_in_process_mcore_static_engine_no_export_no_endpoint_30b_tp4_pp2_ep4_etp1_topk1_greedy_corrected_aime25`;
  - source head `894e2e71e72f09926128e37f22000802804522bc`;
  - selected rank `0`, no best-correct rank selection;
  - total requests `30`, rows `30`, all-request denominator;
  - FT `14/30`, base `15/30`, delta `-1`, disposition `FAIL`.
- Verify prompt/cache/parser/normalizer continuity against task300 accepted
  base evidence, and explicitly assess the sampling-parameter residual.
- Verify boundary confirmations and look for evidence of forbidden actions:
  AIME2025 train data, task255 reuse, training/optimizer steps during task306,
  shared deletion, export/conversion, endpoint launch, promotion, main push, or
  merge.
- Check whether worker_3 has produced an official task306 mailbox/report/PR.
  If absent, state that as a closeout residual and do not invent one.
- Update runbook/provenance wording needed to close the 30B scale-up attempt as
  FAIL/no promotion/no further 30B authorization.

## Boundaries

- Do not train or run optimizer steps.
- Do not rerun AIME2025, non-AIME canary, base eval, export, endpoint, or any
  benchmark.
- Do not use AIME2025 prompts or labels as trainable data.
- Do not reuse task255 artifacts.
- Do not delete shared files, especially under
  `/mnt/cephfs/data/processing/lei.song`.
- Do not push main, merge, approve PRs directly, rewrite worker_3 branches, or
  modify product code.
- Read files, run static git/artifact/checksum inspection commands, and write
  review/runbook docs/status only.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task307_qwen_aime_v11_30b_task306_fail_review_runbook_s1`.
- Review/runbook report:
  `workspace/tasks/task307_qwen_aime_v11_30b_task306_fail_review_runbook_s1/task306_fail_review_runbook_report.md`.
- Mailbox report to lead with:
  - exact #369 PR head, task306 eval source head, and artifact root reviewed;
  - branch/head/PR or mailbox-only status;
  - commands used and output summary;
  - artifact paths, line counts, and checksum verification results;
  - task306 metrics and accepted-base comparison;
  - protocol continuity and sampling-residual assessment;
  - boundary verification;
  - worker_3 closeout/report/PR status and mailbox message ids;
  - approve/request-changes/block decision for lead closeout;
  - final runbook/provenance wording for FAIL/no promotion/no further 30B
    scale-up authorization.

## Acceptance Criteria

- APPROVE_FAIL_CLOSEOUT: task306 final artifacts are internally consistent,
  artifact/checksum/protocol/boundary evidence is complete enough to accept the
  corrected AIME comparison as FAIL, and the runbook/provenance closeout clearly
  blocks promotion/export/endpoint/further 30B scale.
- REQUEST_CHANGES: task306 likely failed below base but report, artifact,
  checksum, protocol, worker closeout, or runbook evidence is incomplete enough
  that lead should request worker fixes before closeout.
- BLOCK: task306 artifacts are invalid, protocol continuity cannot support the
  comparison, or a forbidden action is observed.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Related tasks: task298, task299, task300, task301, task303, task304, task305,
  task306
- Related PRs: #362, #363, #364, #365, #366, #367, #368
- Review target PR: #369
- Current gate: global Qwen AIME 30B gate remains FAIL/HOLD for closeout
  review. No promotion, export, endpoint, new 30B training, or additional
  30B/8-GPU work is authorized.
