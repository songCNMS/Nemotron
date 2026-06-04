# task330 task329 independent review report

## Disposition

Decision: `APPROVE_DOCS_CLOSEOUT_HOLD_TRAINING`.

I independently reviewed #392 exact head
`d911ec58aaa83a0eb92ce19b6f3cbc5575a517cf` and the task329 artifact root
`/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z`.

The task329 evidence is accurate enough to accept as partial docs/evidence
closeout. It is not an expanded all-SFT training contract and does not release
task310. The correct downstream state is HOLD until a later lead-gated
remediation handles the exact blockers below and a combined packed-data
contract is reviewed.

## Review Snapshot

Observed at `2026-06-04T06:24:56Z`.

| Item | Value |
| --- | --- |
| Worker branch | `intern_nemotron_worker_4/task330_qwen_all_sft_task329_independent_review_s1` |
| Review target | PR #392 |
| PR state | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` |
| PR head | `d911ec58aaa83a0eb92ce19b6f3cbc5575a517cf` |
| Base | `origin/main` `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb` |
| Lead docs imported | `e8c9224a3beaff7154a6d08bae26aad724e44310` |
| Artifact root | `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z` |
| Packed root | `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z/packed_qwen_raw_pass_materialized` |

## PR Review

#392 diff scope is worker_2 status plus task329 task docs/report/helper only:

- `workspace/interns/intern_nemotron_worker_2/status.md`
- `workspace/tasks/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/README.md`
- `workspace/tasks/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/build_task329_raw_pass_split_pack_proof.py`
- `workspace/tasks/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/history_log.md`
- `workspace/tasks/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/raw_pass_split_pack_proof_report.md`
- `workspace/tasks/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/task_knowledge.md`

`git diff --check origin/main...origin/pr/392` passed.

The task-local helper compiles via Python `compile()` against the exact PR
blob:

`workspace/tasks/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/build_task329_raw_pass_split_pack_proof.py`

The drift from `e38de2ba` to `48d42bcb` changed worker_2 status and task329
history. The drift from `48d42bcb` to `d911ec58` changed status/session
bookkeeping; the task329 report content changed only the metadata line and the
artifact evidence remained unchanged. Both drift ranges passed
`git diff --check`.

## Artifact Verification

Checksum and contract checks:

| Check | Result |
| --- | --- |
| `sha256sum -c manifests/artifact_checksums.sha256` | PASS, 22 entries |
| `sha256sum -c manifests/packed_shard_checksums.sha256` | PASS, 48 shard files |
| Helper compile from PR blob | PASS |
| `logs/data_prep.rc` | `1`, expected failed-closed symlink attempt |
| `logs/data_prep_materialized.rc` | `0` |
| `logs/qwen30b_contract_validate.rc` | `0` |
| `logs/qwen30b_contract_validate.log` | `QWEN30B_PACKED_CONTRACT=PASS` |

Key manifest checks passed:

- `manifests/final_summary.json`: `PARTIAL_PASS_WITH_EXACT_BLOCKERS`,
  `qwen_contract=PASS`.
- `manifests/qwen30b_packing_metrics.json`: 48 shards, 89,045 packed rows,
  341,849,859 input tokens, 9,490,865 supervised tokens.
- `manifests/packing_receipt_metrics.json`: 75,026 input rows, 91,315 output
  sequences, 89,045 final packed rows, 6 filtered rows.
- `manifests/intended_vs_exposed_parity.json`: `status=PASS`.
- `manifests/decontam_no_aime2025_train_proof.json`:
  `PASS_NO_AIME2025_TRAIN_ROWS_BY_PRIOR_DECONTAM_AND_SOURCE_EXCLUSION`.
- `manifests/combination_decision.json`:
  `COMBINATION_WAITING_FOR_LEAD_REVIEW`.

Packed metrics:

| Split | Shards | Rows | Input tokens | Supervised tokens | Source exposure |
| --- | ---: | ---: | ---: | ---: | --- |
| train | 46 | 84,696 | 326,797,059 | 8,555,986 | all three sources |
| valid | 1 | 2,155 | 7,436,038 | 459,524 | agentic only |
| test | 1 | 2,194 | 7,616,762 | 475,355 | agentic only |
| total | 48 | 89,045 | 341,849,859 | 9,490,865 | three sources in train |

Source metrics:

| Source | Packed rows | Input tokens | Supervised tokens | Exposure |
| --- | ---: | ---: | ---: | --- |
| `agentic-interactive` | 35,323 | 122,527,221 | 7,568,103 | train/valid/test |
| `instruction-following-structured` | 2,693 | 10,307,854 | 1,922,762 | train only |
| `swe` | 51,029 | 209,014,784 | 0 | train only |

## Blocker Review

The three blockers are correctly stated:

1. `task327-swe` produces 51,029 packed rows but `supervised_tokens=0` under
   tokenizer-native Qwen packing. This cannot count as supervised SFT until a
   lead-approved source/config formatter remediation proves nonzero supervised
   tokens.
2. `instruction-following-structured` has 6 validation-filtered rows and 6
   validation errors in receipt metrics. The packed artifact excludes those
   rows, so a later task must review/remediate or explicitly accept the
   exclusion.
3. Valid/test exposure is sparse: train exposes all three sources, while
   valid/test expose only `task322-agentic-interactive`. This must be fixed or
   explicitly accepted before any combined expanded training contract.

All nine task327 `BLOCKED_DECONTAM_HIT` sources are excluded:

- `agentic-tool-calling`
- `competitive-cpp-00`
- `competitive-cpp-01`
- `competitive-python-00`
- `competitive-python-01`
- `infinibyte-00`
- `infinibyte-01`
- `instruction-following-chat`
- `math-proofs-lean`

Included sources have zero prompt-hash, normalized-prompt, and ngram hits in
the carried task322/task327 decontam proof. I found no evidence of AIME2025
prompt/label train rows, task255 reuse, shared deletion, training, eval,
export, endpoint, promotion, merge, self-merge, or main push.

## Recommendation

Approve #392 as `APPROVE_DOCS_CLOSEOUT_HOLD_TRAINING` only.

Required remediation before any task310 release or expanded all-SFT contract:

1. Fix or replace SWE formatting/config so Qwen packing emits nonzero
   supervised tokens, then rerun source metrics, checksum manifests, and Qwen
   contract validation.
2. Resolve the 6 `instruction-following-structured` validation-filtered rows,
   either by remediating them or documenting a lead-accepted exclusion policy.
3. Define and prove per-source valid/test split policy, or obtain explicit
   lead acceptance of sparse valid/test exposure for a bounded purpose.
4. Review any combination with the prior task299 constrained seed in a separate
   lead-gated packed-contract task.
5. Re-run independent review before task310 training, eval, export, endpoint,
   promotion, or downstream benchmark release.

## Commands And Checks

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs +pull/392/head:refs/remotes/origin/pr/392
gh pr view 392 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,title,url
git diff --name-status origin/main...origin/pr/392
git diff --stat origin/main...origin/pr/392
git diff --check origin/main...origin/pr/392
python3 -c "import subprocess; p='workspace/tasks/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/build_task329_raw_pass_split_pack_proof.py'; src=subprocess.check_output(['git','show','origin/pr/392:'+p]); compile(src, p, 'exec'); print('helper_compile=PASS')"
sha256sum -c manifests/artifact_checksums.sha256
sha256sum -c manifests/packed_shard_checksums.sha256
cat logs/data_prep.rc logs/data_prep_materialized.rc logs/qwen30b_contract_validate.rc
sed -n '1,220p' logs/qwen30b_contract_validate.log
python3 <manifest assertion script over final_summary/qwen metrics/receipts/parity/decontam/combination>
gh api repos/songCNMS/Nemotron/issues/392/comments --jq '<lead gate filter>'
git diff --name-status e38de2ba5dd01aacad219f4bfef2e213e3089f44..48d42bcb71ec73cbb9072e696d871e994f8c6a1e
git diff --name-status 48d42bcb71ec73cbb9072e696d871e994f8c6a1e..d911ec58aaa83a0eb92ce19b6f3cbc5575a517cf
git diff --check e38de2ba5dd01aacad219f4bfef2e213e3089f44..48d42bcb71ec73cbb9072e696d871e994f8c6a1e
git diff --check 48d42bcb71ec73cbb9072e696d871e994f8c6a1e..d911ec58aaa83a0eb92ce19b6f3cbc5575a517cf
```

## Boundary Confirmation

I did not edit product code, modify worker_2 branch/artifacts, train, run
optimizer steps, run eval, export, launch endpoint, promote, reuse task255, use
AIME2025 train rows, delete shared files, merge, self-merge, or push main.
Only task330 review docs/status were changed.
