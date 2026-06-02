# task289 Post-Smoke Runbook Provenance Report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_5,SESSION=5 -->

Generated: 2026-06-02T11:11:13Z

## Disposition

Recommendation: `PASS` for docs/runbook provenance only.

The V11 pipeline now has repo-visible packed-data, no-training preflight,
bounded Qwen3-4B smoke, no-export/no-endpoint route-pass, and corrected
AIME2025 metric evidence. Since the prior #351 refresh, #354/task291 merged the
bounded no-export Qwen route pass, #355/task292 merged the independent route
review, and #356/task293 is OPEN/CLEAN/MERGEABLE with the corrected task285
iter2 AIME2025 result.

Task293 reports task285 Qwen3-4B iter2 FT `12/30 = 0.4` against the accepted
task247 Qwen3-4B base comparator `11/30 = 0.36666666666666664`, for delta
`+1/30` and accuracy delta `+0.03333333333333338`. This is a metric pass for
the task293 corrected AIME2025 eval gate only. It does not authorize export,
endpoint launch, promotion, task255 reuse, AIME2025 train-data use, shared
deletion, main push, 30B, or 8-GPU. #356 is not merged in this refresh, and no
task294 branch or PR is visible.

## Provenance

| Item | Value |
|---|---|
| Worker branch | `intern_nemotron_worker_5/task289_qwen_aime_v11_post_smoke_runbook_provenance_s1` |
| Branch base | `origin/main` at `5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0` |
| Current refresh base | `origin/main` at `228ffd741bb9fa4eae6abf8d37bc171397151d7a` |
| Lead docs source | `origin/intern_nemotron_lead/session1-recovery-task-docs` at `70d7aafd0ef4c5073561dcea89cad5fb1d876b6d` |
| Scope | Read-only docs/runbook provenance refresh for task295 on existing #351 |
| Accepted base comparator | Qwen3-4B corrected AIME2025 `11/30 = 0.36666666666666664` |
| Candidate FT metric | task285 iter2 task293 corrected AIME2025 `12/30 = 0.4` |
| Base comparator artifact root | `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z` |
| Base input cache | `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache/aime_score_cache.opencompass_a6ad95f.db` |
| task293 local output root | `/work-agents/intern_nemotron_worker_3/outputs/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z` |
| task293 remote output root | `/root/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z` |

## Provenance Matrix

| Gate | Current evidence | Artifact paths / metrics carried forward | Disposition |
|---|---|---|---|
| task276 packed Qwen data | PR #344 MERGED at `2026-06-02T04:19:38Z`, merge commit `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea`, head `07efab4fa0d8367e96f54af3d2cdc70768d73595` | Packed root `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`; split manifest sha `65501e0eff31cce77ff2d1e36dd915f66fb6b2fd145e0f59701d251e5b7d02c5`; metadata sha `e4ac2157760dd50e50798a9095bf3ea1fb6834e5f405cac2f877560f42dbafd9`; shard checksum list sha `bb6107163f366334468b8db9b8e6ca74f8ddbd612f8b90d3e500e0efa3ba0312` | `PACKED_QWEN_READY_FOR_REVIEW`; sparse valid/test risk carried forward |
| task276 split risk | task276 report records parity PASS and Qwen contract PASS | train `279` rows, valid `1` row, test `0` rows; valid/test sparsity is not model-quality evidence | Accepted provenance risk only |
| task283 no-training preflight | PR #349 MERGED at `2026-06-02T06:03:58Z`, merge commit `f82f8f73c39bc93ff268f45845a94060585b8290`, head `2d042cedb0c4cc448c89d57d7b18986d92361349` | Local root `/work-agents/intern_nemotron_worker_2/outputs/task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1/run_20260602T052346Z`; remote root `/root/task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1/run_20260602T052346Z`; manifest sha `eaf06f61daa5c24e55d94f307abdc02f7870b3ea65d0edfa497625e58bc95ffd`; final log sha `e62a06d815cc0a5f6fbdffd71f6e32668cb02c35b532718eeda2cb5329e790e4` | `CONFIG_IMPORT_PREFLIGHT_PASS_NO_TRAINING_NO_CHECKPOINT_SAVE`; no training or checkpoint save |
| task285 bounded Qwen3-4B smoke | PR #350 MERGED at `2026-06-02T06:53:14Z`, merge commit `5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0`, head `fc379240c8517de10e37a5438f87b6b0994399f0` | Local root `/work-agents/intern_nemotron_worker_2/outputs/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z`; remote run root `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z`; base import log sha `cb1523fffcd97d2b9e5e3b76141624d0d67ad9d2fb1d061e150f15fc7fbf66e6`; retry3 log sha `096e622a94beae16c114afcf6d6cdd923b01f77d4f5a76200b22eed5fcf0767e` | `PASS_SMOKE_EVIDENCE_WITH_POST_TRAIN_EVAL_RC1_RISK`; bounded smoke evidence only |
| task285 optimizer/checkpoint evidence | task285 retry3 ran two optimizer iterations on two visible GPUs after Bridge base import | `CUDA_VISIBLE_DEVICES=0,1`; iter1 LR `3.000000E-07`, loss `1.506399E+00`; iter2 LR `1.000000E-07`, loss `8.874496E-01`; skipped `0`, NaN `0`; checkpoint root `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3`; latest iteration `2`; inventory sha `d4cc3d1e5a047e321e98896996610f1ace0b5c45acd3cbe11bb0a8389ea97b78`; checksum manifest sha `802ef28a30b7ae5a2359b481fc6c8882d1cc2804d0f1edd25cca84973f7794c4` | Reviewable smoke checkpoint only; post-train built-in eval returned RC=1 after SIGTERM |
| task286 independent smoke review | worker_4 branch `origin/intern_nemotron_worker_4/task286_qwen_aime_v11_task285_smoke_gate_review_s1` at `a0db36c1d6831744cd972ac65b90817cfbcfefdc`; history Session 23/24 reviewed #350 exact head | Mailbox `71d5ac1b1bb44bae8163f014563714cf` detailed checksum review; mailbox `9b673d61cf6e4ce5a64d84f7f6198230` confirmed exact-head approval | APPROVE as bounded Qwen3-4B smoke evidence only |
| task287 non-AIME canary failed route | PR #352 MERGED at `2026-06-02T07:39:18Z` as `ca1ab63588651351b3e669450659abd2ad2c73e8` from exact head `52834d74c79ab98b5e125434160843752c34d47a`; report `non_aime_canary_retention_report.md`; disposition `BLOCK` | Candidate checkpoint root `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3`; local output root `/work-agents/intern_nemotron_worker_3/outputs/task287_qwen_aime_v11_non_aime_canary_retention_s1/run_20260602T070403Z`; remote run root `/root/task287_qwen_aime_v11_non_aime_canary_retention_s1/run_20260602T070403Z`; `LOAD_MEGATRON_MODEL=PASS`; final blocker log sha `f32df07a0ab624057a93b3615f28416dc212c3d511bd617fa1c2508825e65473`; blocker json sha `aa451bfb364e1c44b67f6a0beb2612a2f331582555909445099c228c480aab2e` | MERGED BLOCK history: no retained completions, no accepted canary pass |
| task288 canary review | worker_4 branch `origin/intern_nemotron_worker_4/task288_qwen_aime_v11_task287_canary_gate_review_s1` at `a4afc814554f92039d886548a8979cf847e6265e`; no task288 PR found | Session 27 reviewed #352 exact head, verified report sha `9d88a9f7fce7c7904adccedc924f881b51bb4471988785283b6460396600846e`, and mailed decision `APPROVE_BLOCKER_CLOSEOUT` as `a7667e01d0cb4188aa0e5dc222ae7da0` | APPROVED BLOCKER EVIDENCE ONLY |
| task290 blocker review | PR #353 MERGED at `2026-06-02T07:52:08Z` as `a372dcd7cd866dc02951f4f1c86eaf05a4c885b4` from exact head `daad63efe77f19b8d56c62eca9d9f9331efd6e22`; lead approval comment `4599915303` approved exact head as read-only blocker review docs/evidence only | Review report `task287_blocker_review_report.md`; decision `APPROVE_BLOCKER_CLOSEOUT`; reviewed #352 exact head; required hashes matched; no retained completion artifacts found; recommended bounded no-export/no-endpoint route-unblock task | MERGED BLOCKER REVIEW; no AIME/task243 release by itself |
| task291 route unblock | PR #354 MERGED at `2026-06-02T08:30:04Z` as `34de04ff06cc2921ef1c65cde347b1f6e1b54bcf` from head `2fda1ed46da4c82712a5c22c85bf124c26c6376f` | Artifact root `/work-agents/intern_nemotron_worker_2/outputs/task291_qwen_aime_v11_no_export_canary_route_unblock_s1/run_20260602T081136Z`; route `direct_in_process_mcore_static_engine_no_export_no_endpoint_topk1_greedy`; `5` synthetic non-AIME prompts retained; exact matches `5/5`; canary summary sha `dd855c2c32b0b7411ee1cd365311363f1d3338753560107768b684b8fb660d40`; checksum manifest sha `08477bf8be669314a54359edeeca16de4605262ce5d553944e3477e4ff46f97d` | MERGED ROUTE PASS for non-AIME canary route only |
| task292 route review | PR #355 MERGED at `2026-06-02T08:37:35Z` as `228ffd741bb9fa4eae6abf8d37bc171397151d7a` from head `e519fecc1065bd055a69fdf271bd21994facd13b` | Review report `task291_canary_route_review_report.md`; decision `APPROVE_CANARY_ROUTE_PASS`; recomputed all files listed in task291 checksum manifest and all matched; boundary confirmation recorded no canary rerun, training, AIME/task243 eval, export, endpoint, promotion, task255 reuse, shared deletion, 30B, or 8-GPU action | MERGED INDEPENDENT ROUTE REVIEW; residual detokenized fallback risk carried |
| task293 corrected AIME2025 eval | PR #356 OPEN/base main/CLEAN/MERGEABLE at head `672d0101681a5d9c4b6c34814c75fcc0d97b4fcb`; report `task285_iter2_same_harness_aime_eval_report.md`; run source head `87de0a97e6c0406a4b67520faab6b11d91d9131e`; run id `run_20260602T085237Z` | Candidate checkpoint `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3/iter_0000002`; base/tokenizer `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`; local output root `/work-agents/intern_nemotron_worker_3/outputs/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z`; FT `12/30 = 0.4`; base `11/30 = 0.36666666666666664`; parsed rows `21/30`; request status `30/30 ok` | PASS for corrected AIME eval metric only; #356 not merged and task294 review not visible |
| task293 artifact hashes | task293 local copied artifacts have recorded sha256 checksums | `artifacts/aime_eval/summary.json` sha `64a378ca54534ec426b92a7b6bc436edb4fddd2ea1ba831f61afeed4e1ad39b7`; `results.jsonl` sha `4cbc2a9543a658df6a3e18e3128c5a5c9a173f9a575372095cfcbe5d6232aca5`; `full_completions.jsonl` sha `5cb1e11ab8d331127c7c12f2cd8c04d83d2e6bd93445a5ebffc62363e2a818b4`; checksum manifest sha `6a47e802433648248658010125db51474d0b4af565dc10c637d004900948e7d4`; prompt manifest sha `93146086fcc2214fc3c866354e23358d320377caddb6d2b5a2bd58954e85b919`; checkpoint load manifest sha `243044f2e548e0c8b1b539e9c11fee17a39b4d45898e1a6601382716e4d90c74`; command env manifest sha `5b128b5cc84159b8603b07fc92475ebc768152b7c0ea0fae0897c6635a502ccf` | Reviewable task293 artifacts recorded |
| task294 independent review | `gh pr list --state all --search task294` and `git ls-remote --heads origin '*task294*'` found no task294 PR or branch | No repo-visible task294 review report exists in this refresh | HOLD_PENDING_REVIEW |

## Stage State

| Stage | Status | Reason |
|---|---|---|
| Packed data | `PASS_PROVENANCE` | #344/task276 merged packed Qwen evidence with carried sparse valid/test risk |
| No-training runtime preflight | `PASS_NO_TRAINING` | #349/task283 merged config/import preflight PASS without training/checkpoint save |
| Bounded Qwen3-4B smoke | `PASS_SMOKE_ONLY` | #350/task285 merged two-step nonzero-LR finite-loss checkpoint evidence; task286 approved smoke-only |
| Non-AIME canary failed route | `BLOCKER_CLOSED` | #352/task287 merged BLOCK and task288/#353-task290 approved blocker closeout as evidence only |
| No-export local route proof | `PASS_ROUTE_PROOF` | #354/task291 merged retained synthetic non-AIME completions `5/5`; #355/task292 independently approved the pass |
| Corrected AIME2025 metric | `PASS_EVAL_GATE_ONLY` | #356/task293 reports task285 iter2 FT `12/30 = 0.4` versus accepted base `11/30 = 0.36666666666666664` |
| task293 publication / task294 review | `HOLD_PENDING_REVIEW` | #356 is open and task294 independent review is not repo-visible |
| Promotion / export / endpoint / 30B / 8-GPU | `NO-GO` | no release clearance; task293 pass is not promotion or scale authorization |

## Read-Only Checks Performed

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs \
  intern_nemotron_worker_3/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1 \
  intern_nemotron_worker_4/task292_qwen_aime_v11_task291_canary_route_review_s1
git rev-parse origin/main origin/intern_nemotron_lead/session1-recovery-task-docs \
  origin/intern_nemotron_worker_3/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1 \
  origin/intern_nemotron_worker_4/task292_qwen_aime_v11_task291_canary_route_review_s1
gh pr view 351 --json number,state,baseRefName,headRefName,headRefOid,mergeable,isDraft,title,url
gh pr view 354 --json number,state,headRefName,headRefOid,mergeCommit,mergedAt,title,url
gh pr view 355 --json number,state,headRefName,headRefOid,mergeCommit,mergedAt,title,url
gh pr view 356 --json number,state,baseRefName,headRefName,headRefOid,mergeable,isDraft,title,url
gh pr list --state all --search task294 --json number,state,headRefName,headRefOid,mergeable,title,url,updatedAt --limit 20
git ls-remote --heads origin '*task294*' '*task292*' '*task293*'
git show origin/intern_nemotron_worker_3/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1:workspace/tasks/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/task285_iter2_same_harness_aime_eval_report.md
git show origin/intern_nemotron_worker_4/task292_qwen_aime_v11_task291_canary_route_review_s1:workspace/tasks/task292_qwen_aime_v11_task291_canary_route_review_s1/task291_canary_route_review_report.md
```

These were provenance reads only. No runtime, training, canary execution,
AIME re-eval, task243 eval, export, endpoint, artifact mutation, shared
deletion, merge, main push, 30B, or 8-GPU action was performed.

## Same-Harness Proof Summary

- task293 used the accepted task247 AIME source cache and base artifact root.
- Prompt-token proof against task247 base had `0` mismatches across all `30`
  rows.
- Same prompt variant `original`, same max-token cap `8192`, same corrected
  row count and denominator `30`, and same copied task247 parser/normalizer
  functions: `boxed_values`, `normalize_answer`, `correct`, and
  `contains_expected`.
- task293 used a no-export/no-endpoint in-process MCore static engine with
  `CUDA_VISIBLE_DEVICES=0`, one visible H200, `top_k=1`, temperature `1.0`,
  `top_p=0.0`, and seed `1234`.
- AIME2025 prompts and labels were held out for eval/decontamination evidence
  only. They are not trainable data.
- task255 remains discarded and must not be reused.

## Residual Risks

- task276 valid/test splits remain sparse: valid has one packed row and test has
  zero rows. This is carried provenance risk, not quality evidence.
- task285 retry3 returned RC=1 after the iter2 checkpoint save when the
  framework entered built-in validation and was terminated. It is not a clean
  end-to-end train/eval pass and its built-in validation output is unusable.
- #352/task287 is still the historical failed canary-route record. #354/task291
  supersedes it for the no-export local route with retained synthetic non-AIME
  completions, but the failed route remains provenance context.
- task292 carries a narrow residual risk: the
  `synthetic_word_completion_ready_set` row used
  `generated_tokens_detokenize_fallback` because MCore `generated_text` was
  empty while generated token ids decoded to retained text.
- task293 reports `sampling_exact_parameter_match=false`: the FT eval used the
  no-export/no-endpoint MCore greedy route, while the accepted base comparator
  used SGLang `/v1/chat/completions`. Prompt tokenization, cache, parser,
  denominator, max-token cap, and deterministic greedy intent match; transport
  and sampling surfaces are not byte-identical.
- #356/task293 is OPEN/CLEAN/MERGEABLE but not merged in this refresh.
- No task294 branch or PR is visible, so independent task293 review remains
  pending/not visible.

## No-Clearance Statement

This report is documentation only. It records that task293 has an eval-metric
pass over the accepted base comparator. It does not authorize or claim clearance
for additional training, AIME re-eval, task243 evaluation, export, endpoint
launch, promotion, task255 reuse, AIME2025 train-data use, shared-file deletion,
merge, main push, 30B, or 8-GPU.
