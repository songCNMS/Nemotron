# task295_qwen_aime_v11_post_aime_pass_runbook_refresh_s1 - task knowledge

- task293 read-only artifacts show V11 task285 Qwen3-4B iter2 corrected AIME2025
  `12/30 = 0.4`, which is above accepted base `11/30`.
- This is a metric pass only. It does not authorize export, endpoint, promotion,
  30B, or 8-GPU.
- #351/task289 predates task293 and is stale/HOLD until refreshed or superseded.
- Runbook must preserve residual risks: task293 sampling semantic-match review,
  task292 canary fallback risk, worker_3 official closeout status, and task294
  independent review status.
- #351 head `6d4b6ac` was refreshed but remained stale after #357/#356 merged.
  Lead request-changes/HOLD comment `4601906134` required a new refresh against
  current main `31a3e962...`.
- #351 head `c2c217231c9d377430171166c85d1165ac75db69` now records #357/#356
  merged state, task293 FT `12/30 = 0.4` versus base `11/30`, artifact roots and
  checksums, residual risks, and no-clearance boundaries.
- Lead approval/HOLD-lift comment `4601969623` permits worker_5 self-merge only
  if #351 remains exact head `c2c2172...` and CLEAN/MERGEABLE at merge time.
- #351 merged at `2026-06-02T11:35:48Z` with merge commit
  `5d8b8d850d26e785332f8b707c772d99881a1b5d` from approved head
  `c2c217231c9d377430171166c85d1165ac75db69`.
- Task295 is completed as docs/provenance closeout only. No export, endpoint,
  promotion, further training/eval, task255 reuse, AIME2025 train data, shared
  deletion, 30B, or 8-GPU is authorized by #351.
- worker_5 closeout mailbox `d27a39d8b1144952921d2eae26c7f9e3` confirms #351
  merged only after exact-head clean verification and that no forbidden runtime,
  eval, release, scale, data-use, or artifact-mutation action occurred.
