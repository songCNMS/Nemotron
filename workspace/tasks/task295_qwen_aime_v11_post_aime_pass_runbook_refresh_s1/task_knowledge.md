# task295_qwen_aime_v11_post_aime_pass_runbook_refresh_s1 - task knowledge

- task293 read-only artifacts show V11 task285 Qwen3-4B iter2 corrected AIME2025
  `12/30 = 0.4`, which is above accepted base `11/30`.
- This is a metric pass only. It does not authorize export, endpoint, promotion,
  30B, or 8-GPU.
- #351/task289 predates task293 and is stale/HOLD until refreshed or superseded.
- Runbook must preserve residual risks: task293 sampling semantic-match review,
  task292 canary fallback risk, worker_3 official closeout status, and task294
  independent review status.
- #351 head `6d4b6ac` was refreshed but remains stale after #357/#356 merged.
  Lead request-changes/HOLD comment `4601906134` requires a new refresh against
  current main `31a3e962...`.
