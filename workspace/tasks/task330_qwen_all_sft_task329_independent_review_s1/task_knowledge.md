# task330_qwen_all_sft_task329_independent_review_s1 - task knowledge

<!-- METADATA:SESSION=82 -->

1. #392 exact head for review is
   `d911ec58aaa83a0eb92ce19b6f3cbc5575a517cf`; do not review a drifting head
   without lead confirmation.
2. task329 artifact root is
   `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z`.
3. Lead preliminary verification found checksum manifests pass and
   `QWEN30B_PACKED_CONTRACT=PASS`, but the final summary is
   `PARTIAL_PASS_WITH_EXACT_BLOCKERS`.
4. Known blockers to verify: SWE supervised tokens are zero, structured source
   has 6 validation-filtered rows, and valid/test split exposure is sparse.
5. Any approval is docs/evidence closeout only; task310 training and all eval
   remain blocked until a later lead-gated remediation and combined contract
   review.
6. Current authoritative lead gate comment is `issuecomment-4619497556`.
   Earlier comments `issuecomment-4619456297` and `issuecomment-4619471068`
   were superseded after metadata-only head drift.
