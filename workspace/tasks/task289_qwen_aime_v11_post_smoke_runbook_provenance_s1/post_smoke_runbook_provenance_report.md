# task289 Post-Smoke Runbook Provenance Report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_5,SESSION=2 -->

Generated: 2026-06-02T07:37:27Z

## Disposition

Recommendation: `PASS` for docs/runbook provenance only.

The V11 pipeline has repo-visible packed-data, no-training preflight, and
bounded Qwen3-4B smoke evidence. This report updates the provenance matrix after
#349/task283 and #350/task285 merged, and after task286 approved #350 as
bounded smoke evidence only. It also records #352/task287 as official
non-AIME canary BLOCK evidence: checkpoint load proof passed, but the run
retained no completions and produced no accepted canary pass. task288 and
task290 are still pending review inputs for that blocker evidence.

Corrected AIME2025 same-harness FT-vs-base comparison remains blocked until
the task287 blocker is resolved with accepted non-AIME canary evidence,
task288/task290/lead review is processed, and lead explicitly releases the
AIME/task243 task. This report does not authorize training, canary execution,
AIME/task243 eval, export, endpoint, promotion, task255 reuse, AIME2025 train
data, shared deletion, merge, main push, 30B, or 8-GPU.

## Provenance

| Item | Value |
|---|---|
| Worker branch | `intern_nemotron_worker_5/task289_qwen_aime_v11_post_smoke_runbook_provenance_s1` |
| Branch base | `origin/main` at `5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0` |
| Lead docs source | `origin/intern_nemotron_lead/session1-recovery-task-docs` at `3178c4044d9acc5d930d356516ebd737f548d158` |
| Scope | Read-only docs/runbook provenance refresh |
| Accepted base comparator | Qwen3-4B corrected AIME2025 `11/30 = 0.36666666666666664` |
| Base comparator artifact root | `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z` |
| Base input cache | `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache/aime_score_cache.opencompass_a6ad95f.db` |

## Provenance Matrix

| Gate | Current evidence | Artifact paths / metrics carried forward | Disposition |
|---|---|---|---|
| task276 packed Qwen data | PR #344 MERGED at `2026-06-02T04:19:38Z`, merge commit `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea`, head `07efab4fa0d8367e96f54af3d2cdc70768d73595` | Packed root `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`; split manifest sha `65501e0eff31cce77ff2d1e36dd915f66fb6b2fd145e0f59701d251e5b7d02c5`; metadata sha `e4ac2157760dd50e50798a9095bf3ea1fb6834e5f405cac2f877560f42dbafd9`; shard checksum list sha `bb6107163f366334468b8db9b8e6ca74f8ddbd612f8b90d3e500e0efa3ba0312` | `PACKED_QWEN_READY_FOR_REVIEW`; sparse valid/test risk carried forward |
| task276 split risk | task276 report records parity PASS and Qwen contract PASS | train `279` rows, valid `1` row, test `0` rows; valid/test sparsity is not model-quality evidence | Accepted provenance risk only |
| task283 no-training preflight | PR #349 MERGED at `2026-06-02T06:03:58Z`, merge commit `f82f8f73c39bc93ff268f45845a94060585b8290`, head `2d042cedb0c4cc448c89d57d7b18986d92361349` | Local root `/work-agents/intern_nemotron_worker_2/outputs/task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1/run_20260602T052346Z`; remote root `/root/task283_qwen_aime_v11_bridge_runtime_remediation_preflight_s1/run_20260602T052346Z`; manifest sha `eaf06f61daa5c24e55d94f307abdc02f7870b3ea65d0edfa497625e58bc95ffd`; final log sha `e62a06d815cc0a5f6fbdffd71f6e32668cb02c35b532718eeda2cb5329e790e4` | `CONFIG_IMPORT_PREFLIGHT_PASS_NO_TRAINING_NO_CHECKPOINT_SAVE`; no training or checkpoint save |
| task285 bounded Qwen3-4B smoke | PR #350 MERGED at `2026-06-02T06:53:14Z`, merge commit `5d32f07698249d9d352e7ba6da9c6d3bd88eb3f0`, head `fc379240c8517de10e37a5438f87b6b0994399f0` | Local root `/work-agents/intern_nemotron_worker_2/outputs/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z`; remote run root `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z`; base import log sha `cb1523fffcd97d2b9e5e3b76141624d0d67ad9d2fb1d061e150f15fc7fbf66e6`; retry3 log sha `096e622a94beae16c114afcf6d6cdd923b01f77d4f5a76200b22eed5fcf0767e` | `PASS_SMOKE_EVIDENCE_WITH_POST_TRAIN_EVAL_RC1_RISK`; bounded smoke evidence only |
| task285 optimizer/checkpoint evidence | task285 retry3 ran two optimizer iterations on two visible GPUs after Bridge base import | `CUDA_VISIBLE_DEVICES=0,1`; iter1 LR `3.000000E-07`, loss `1.506399E+00`; iter2 LR `1.000000E-07`, loss `8.874496E-01`; skipped `0`, NaN `0`; checkpoint root `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3`; latest iteration `2`; inventory sha `d4cc3d1e5a047e321e98896996610f1ace0b5c45acd3cbe11bb0a8389ea97b78`; checksum manifest sha `802ef28a30b7ae5a2359b481fc6c8882d1cc2804d0f1edd25cca84973f7794c4` | Reviewable smoke checkpoint only; post-train built-in eval returned RC=1 after SIGTERM |
| task286 independent smoke review | worker_4 branch `origin/intern_nemotron_worker_4/task286_qwen_aime_v11_task285_smoke_gate_review_s1` at `a0db36c1d6831744cd972ac65b90817cfbcfefdc`; history Session 23/24 reviewed #350 exact head | Mailbox `71d5ac1b1bb44bae8163f014563714cf` detailed checksum review; mailbox `9b673d61cf6e4ce5a64d84f7f6198230` confirmed exact-head approval | APPROVE as bounded Qwen3-4B smoke evidence only; eligible only for a separately authorized non-AIME canary gate |
| task287 non-AIME canary | PR #352 OPEN/base main/CLEAN at exact head `52834d74c79ab98b5e125434160843752c34d47a`; report `non_aime_canary_retention_report.md`; disposition `BLOCK` | Candidate checkpoint root `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3`; local output root `/work-agents/intern_nemotron_worker_3/outputs/task287_qwen_aime_v11_non_aime_canary_retention_s1/run_20260602T070403Z`; remote run root `/root/task287_qwen_aime_v11_non_aime_canary_retention_s1/run_20260602T070403Z`; `LOAD_MEGATRON_MODEL=PASS`; prompt source sha `150ee11dc6e8efd3c865a8e9ed8a9ab8ce4f5ee032bed383c73a6cea34f52f1c`; prompt manifest sha `69d6634c47eea160548fe2779b6dd6038dc7605e8c9a894660a385efc9ae7cc2`; final blocker log sha `f32df07a0ab624057a93b3615f28416dc212c3d511bd617fa1c2508825e65473`; blocker json sha `aa451bfb364e1c44b67f6a0beb2612a2f331582555909445099c228c480aab2e` | BLOCK: no retained completions, `canary_summary.json` absent, retained completion rows `0`, correct canary answers `0/5`; no accepted canary pass |
| task288 canary review | worker_4 branch `origin/intern_nemotron_worker_4/task288_qwen_aime_v11_task287_canary_gate_review_s1` at `e62fad1da9a4279869e939a34604c4f1ce13827b`; no task288 PR found | task288 accepted the review task before #352 existed; it has not yet approved #352 exact head | HOLD pending current-head task287 blocker review |
| task290 blocker review | worker_1 branch `origin/intern_nemotron_worker_1/task290_qwen_aime_v11_task287_blocker_review_s1` at `dab9a8bb87315bed529af0f00e3c843b1f910d0e`; no task290 PR found | task docs assign independent read-only review of task287 blocker artifacts and #352 exact head `52834d74c79ab98b5e125434160843752c34d47a` | HOLD pending independent blocker review |
| Corrected AIME2025 FT-vs-base | Accepted same-harness base comparator from task247/task257 remains Qwen3-4B `11/30 = 0.36666666666666664` | Base artifact root and cache listed above; base cache sha `c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74`; base summary sha `376f189c69a8b13fc7752f2f8c362a734154d43fe717209dedf6d0d1649d8639` | BLOCKED until task287 blocker is resolved, task288/task290/lead process reviews, and lead explicitly releases AIME/task243 |

## Stage State

| Stage | Status | Reason |
|---|---|---|
| Packed data | `PASS_PROVENANCE` | #344/task276 merged packed Qwen evidence with carried sparse valid/test risk |
| No-training runtime preflight | `PASS_NO_TRAINING` | #349/task283 merged config/import preflight PASS without training/checkpoint save |
| Bounded Qwen3-4B smoke | `PASS_SMOKE_ONLY` | #350/task285 merged two-step nonzero-LR finite-loss checkpoint evidence; task286 approved smoke-only |
| Non-AIME canary/completion retention | `BLOCKED` | #352/task287 official report is BLOCK with no retained completions and no accepted pass |
| Independent canary/blocker review | `REVIEW_PENDING` | task288 and task290 current-head reviews are pending |
| Same-harness AIME comparison | `BLOCKED` | requires task287 blocker resolution, task288/task290/lead processing, and explicit lead AIME/task243 release |
| Promotion / export / endpoint / 30B / 8-GPU | `NO-GO` | no clearance and no qualifying AIME comparison artifact |

## Read-Only Checks Performed

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git rev-parse origin/main origin/intern_nemotron_lead/session1-recovery-task-docs
gh pr view 344 --json number,state,headRefOid,mergeCommit,mergedAt,baseRefName,title,url
gh pr view 349 --json number,state,headRefOid,mergeCommit,mergedAt,baseRefName,title,url
gh pr view 350 --json number,state,headRefOid,mergeCommit,mergedAt,baseRefName,title,url
gh pr view 351 --json number,state,headRefOid,mergeable,mergeStateStatus,baseRefName,title,url
gh pr view 352 --json number,state,headRefOid,mergeable,mergeStateStatus,baseRefName,title,url
git ls-remote origin '*task286*' '*task287*' '*task288*' '*task290*'
git fetch origin intern_nemotron_worker_4/task286_qwen_aime_v11_task285_smoke_gate_review_s1
git fetch origin intern_nemotron_worker_3/task287_qwen_aime_v11_non_aime_canary_retention_s1
git fetch origin intern_nemotron_worker_4/task288_qwen_aime_v11_task287_canary_gate_review_s1
git fetch origin intern_nemotron_worker_1/task290_qwen_aime_v11_task287_blocker_review_s1
git show origin/intern_nemotron_worker_3/task287_qwen_aime_v11_non_aime_canary_retention_s1:workspace/tasks/task287_qwen_aime_v11_non_aime_canary_retention_s1/non_aime_canary_retention_report.md
git show origin/intern_nemotron_worker_4/task288_qwen_aime_v11_task287_canary_gate_review_s1:workspace/tasks/task288_qwen_aime_v11_task287_canary_gate_review_s1/history_log.md
git show origin/intern_nemotron_worker_1/task290_qwen_aime_v11_task287_blocker_review_s1:workspace/tasks/task290_qwen_aime_v11_task287_blocker_review_s1/README.md
find /work-agents/intern_nemotron_worker_2/outputs -maxdepth 3 -type f | rg 'task283|task285|task276'
find /work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1 -maxdepth 3 -type f
```

These were provenance reads only. No runtime, training, canary, eval, export,
endpoint, artifact mutation, shared deletion, merge, main push, 30B, or 8-GPU
action was performed.

## Residual Risks

- task276 valid/test splits remain sparse: valid has one packed row and test has
  zero rows. This is carried provenance risk, not quality evidence.
- task285 retry3 returned RC=1 after the iter2 checkpoint save when the
  framework entered built-in validation and was terminated. It is not a clean
  end-to-end train/eval pass and its built-in validation output is unusable.
- #352/task287 is an official BLOCK record, not a canary pass. It retained no
  completions and produced no accepted canary summary/result files.
- task288 and task290 have not approved #352/task287. They are the pending
  independent review gates for the blocker evidence.
- No V11 corrected AIME2025 same-harness FT result exists. The accepted base
  comparator is available, but FT-vs-base judgment is blocked.

## No-Clearance Statement

This report is documentation only. It does not authorize or claim clearance for
additional training, non-AIME canary execution, AIME/task243 evaluation, export,
endpoint launch, promotion, task255 reuse, AIME2025 train-data use, shared-file
deletion, merge, main push, 30B, or 8-GPU.
