# task305 task304 canary review report

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_4,SESSION=1 -->

## Decision

Decision: `APPROVE_TASK304_NON_AIME_CANARY_PASS_WITH_RESIDUALS`.

Lead may accept task304 as bounded synthetic non-AIME checkpoint-load and
completion-retention canary evidence for the task301 `iter_0000035` salvage
checkpoint. This does not approve #367 directly, does not clear corrected
AIME2025/task243, does not clear FT-vs-base comparison, and does not authorize
export, endpoint, promotion, additional training, task255 reuse, AIME2025 train
data use, shared deletion, main push, or merge.

## Reviewed Inputs

- PR: #367 `https://github.com/songCNMS/Nemotron/pull/367`
- Exact reviewed head:
  `1f23d8339c123702eaa9336c1fe2b25afcd6122a`
- PR state at review: `OPEN`, base `main`, `CLEAN`, `MERGEABLE`, non-draft.
- Evidence source head in task304 report:
  `d8e58461ca1cede2569589f95414c360e0ddd9bc`
- Refreshed lead docs:
  `origin/intern_nemotron_lead/session1-recovery-task-docs`
  `e39bc08b6f00bfaf21bd68da989fac32e2eb439a`
- Task304 report:
  `workspace/tasks/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/30b_salvage_non_aime_canary_report.md`
- Local artifact root:
  `/work-agents/intern_nemotron_worker_3/outputs/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_20260602T175458Z`
- Remote artifact root checked read-only:
  `/root/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_20260602T175458Z`

## Commands And Checks

Read-only commands included:

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs intern_nemotron_worker_3/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1
gh pr view 367 --json number,state,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,isDraft,files,url
git diff --name-status origin/main...1f23d8339c123702eaa9336c1fe2b25afcd6122a
git diff --check origin/main...1f23d8339c123702eaa9336c1fe2b25afcd6122a
git diff --name-status d8e58461ca1cede2569589f95414c360e0ddd9bc..1f23d8339c123702eaa9336c1fe2b25afcd6122a
git diff --check d8e58461ca1cede2569589f95414c360e0ddd9bc..1f23d8339c123702eaa9336c1fe2b25afcd6122a
git diff --name-status 773aff2cc9eaa7d0900b06f5d49dc29515cae709..a38abd53c897b3c68878abb770cb80f762c20e6f
git diff --check 773aff2cc9eaa7d0900b06f5d49dc29515cae709..a38abd53c897b3c68878abb770cb80f762c20e6f
git diff --name-status a38abd53c897b3c68878abb770cb80f762c20e6f..e5cc49821d39a014756dfd3ce961bab351a4f0fe
git diff --check a38abd53c897b3c68878abb770cb80f762c20e6f..e5cc49821d39a014756dfd3ce961bab351a4f0fe
git diff --name-status e5cc49821d39a014756dfd3ce961bab351a4f0fe..1f23d8339c123702eaa9336c1fe2b25afcd6122a
git diff --check e5cc49821d39a014756dfd3ce961bab351a4f0fe..1f23d8339c123702eaa9336c1fe2b25afcd6122a
sha256sum -c <named task305 checksum list>
jq -r '.files[] | "\(.sha256)  \(.relative_path)"' artifacts/manifests/checksum_manifest.json | sha256sum -c -
python3 - <<'PY'
# Parse summary, decision, prompt manifest, rank summaries, rank result rows,
# rank completion rows, command/env manifests, and checkpoint-load manifests.
PY
ssh NemTron '... read-only remote root key hash checks ...'
```

No training, canary rerun, AIME/task243/corrected AIME, benchmark eval, export,
endpoint, promotion, task255 reuse, AIME2025 train data use, shared deletion,
main push, merge, direct #367 approval, worker_3 branch rewrite, or product-code
modification was performed.

## PR Scope And Head Drift

#367 exact head `1f23d8339c123702eaa9336c1fe2b25afcd6122a` changes only:

- `workspace/interns/intern_nemotron_worker_3/status.md`
- task304 README/history/task_knowledge/report
- task304 runner
  `workspace/tasks/task304_qwen_aime_v11_30b_salvage_non_aime_canary_s1/run_30b_no_export_canary_probe.py`

`git diff --check` passed for the PR diff and all requested drift ranges.

The evidence source `d8e58461..1f23d833` delta is task304 report/docs/status/
hygiene closeout. The final refresh ranges are narrower:

- `773aff2c..a38abd53`: worker_3 status plus task304 history only.
- `a38abd53..e5cc4982`: worker_3 status plus task304 history/task_knowledge
  HOLD bookkeeping only.
- `e5cc4982..1f23d833`: worker_3 status plus task304 history/task_knowledge
  no-further-head-changes bookkeeping only.

I found no unrelated product training/eval path changes in #367.

## Artifact Checksums

All named task305 checksums matched locally, including:

- `artifacts/canary/canary_summary.json`
  `be1a1b544a8f007c4ffceaa5dc758434f8452b4dace0c4f054ca43c8d9ca7c5f`
- `artifacts/canary/canary_decision.json`
  `7678a8f8f3445882a1e5ea575169d37aae7f7ad9ead14b4f5d788fa5c5cb3ba5`
- `artifacts/canary/canary_results.jsonl`
  `35bde0394601c94a278c81600ab9fd5039ac9985ea47219226a138041f81a462`
- `artifacts/canary/canary_full_completions.jsonl`
  `7589dced789173f3956712ca0c0c17215e03d90cb71419ce22209d8aa9bad957`
- `artifacts/manifests/canary_prompt_manifest.json`
  `7b8de981e7d55bd146c557edffd689ed7d1c4af76a14037a0bdfa7770f262da5`
- `artifacts/manifests/checkpoint_load_manifest_rank0.json`
  `2989b432df6e804c6afe11e86ee0baafaed1ea42c2d6b24f9de1317abb92d901`
- `artifacts/manifests/command_env_manifest_rank0.json`
  `d5e282347975d510d2d58b57f26dd8628566d16893b0cd41aba2a8f7a3ee55d8`
- `artifacts/manifests/checksum_manifest.json`
  `0bdbdd6cc28c7c76d6966d1e60832f048c7eb64dff3931c84e269c1a1c2be27b`
- `artifacts/logs/ranks/rank00_events.jsonl`
  `702b1640e2861b45a7811e0bfc31fa705f2b8cca9fc413b7b85cd797f4b26132`
- `logs/remote_no_export_canary.log`
  `18d8dbd021f72f4117f0e183da910a6242ca5d75efe6509816c54a09f5f6d872`
- `logs/remote_no_export_canary_command.txt`
  `83721a5516e716452427e1c72cea3a67fca4f533a418872b3f1cc688b1e9ac20`
- `logs/remote_no_export_canary.rc`
  `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`

I also replayed the full local
`artifacts/manifests/checksum_manifest.json`; every listed canary, rank,
checkpoint-load, command/env, and rank-event file returned `OK`.

Remote root existed. The remote key artifact, command, and rc hashes matched.
Remote root did not include the local copied files
`logs/remote_no_export_canary.log` and `logs/local_source_prompt_hashes.sha256`;
those files are present and checksum-verified in the local artifact root. Remote
`jq` was unavailable, so I did not replay the full checksum manifest remotely.

## Canary Metrics

The parsed canary summary and decision artifacts support PASS:

- disposition: `PASS`
- canary pass: `true`
- `remote_no_export_canary.rc`: `0`
- prompts requested: `5`
- retained completions: `5`
- non-empty responses: `5`
- exact expected-answer matches: `5/5`
- final-answer marker count: `9`
- empty responses: `0`
- mixed-script count: `0`
- degeneration count: `0`
- missing prompt ids: `[]`
- failed prompt ids: `[]`
- aggregate results rows: `5`
- aggregate full-completion rows: `5`
- each rank result file rows: `5`
- each rank full-completion file rows: `5`

Each checked prompt status was `ok`:

- `synthetic_arithmetic_sum_37_58`: expected/extracted `95`
- `synthetic_counting_pens_6_9`: expected/extracted `15`
- `synthetic_linear_expression_2x_plus_y`: expected/extracted `29`
- `synthetic_next_integer_246`: expected/extracted `247`
- `synthetic_word_completion_ready_set`: expected/extracted `go`

## Checkpoint-Load Proof

All rank checkpoint-load manifests report:

- `load_megatron_model`: `PASS`
- model dtype: `torch.bfloat16`
- model eval: `true`
- tensor parallel: `4`
- pipeline parallel: `2`
- expert parallel: `4`
- expert tensor parallel: `1`
- sequence parallel: `true`

Rank0 events record the effective loader `mp_overrides` with TP4/PP2/EP4/ETP1,
CP1, and sequence parallel true.

## Prompt Provenance And Boundary Checks

The prompt source in PR head `1f23d833` hashes to:
`150ee11dc6e8efd3c865a8e9ed8a9ab8ce4f5ee032bed383c73a6cea34f52f1c`.

The prompt manifest confirms:

- prompt set id `qwen_v11_non_aime_export_load_canary_v1`
- `synthetic_prompts_only=true`
- `excludes_aime2025=true`
- `excludes_training_rows=true`
- `review_only_not_trainable=true`
- `no_aime2025_prompt_or_label_text=true`

Command/env and summary boundary confirmations were all true:

- no AIME2025 train prompts or labels
- no AIME/task243 eval
- no endpoint
- no export or conversion
- no main push or merge
- no promotion
- no shared deletion
- no task255 reuse
- no training or optimizer steps
- Qwen3-30B only

## Residual Risks

- This is a five-prompt synthetic non-AIME canary only. It is not benchmark
  quality evidence.
- The task301 checkpoint remains a salvage candidate because task301 ended with
  validation incomplete and `train_rc=1`.
- The route is no-export MCore greedy-route evidence using `top_k=1`,
  `temperature=1.0`, `top_p=0.0`; it is not endpoint equivalence.
- `command_env_manifest_rank0.json` lacks a separate `mp_overrides` field, but
  rank event logs and checkpoint-load manifests prove the effective parallelism.
- Corrected AIME2025/task243 FT-vs-base comparison against the base 30B score
  remains blocked until lead creates a separate evaluation task.

## Final Verdict

Approve task304 as bounded synthetic non-AIME checkpoint-load and
completion-retention canary evidence only, with residuals above. Do not treat
this as #367 direct approval, corrected AIME2025/task243 clearance, export or
endpoint clearance, promotion clearance, additional training clearance, or a
30B go/no-go decision.
