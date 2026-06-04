# task328_qwen_all_sft_post_task327_packed_contract_s1 - task knowledge

<!-- METADATA:SESSION=80 -->

1. task309/#372 is merged as a packed-contract blocker and predates task322 and
   task327 final source evidence; task328 is the successor packed-contract task.
2. task327/#390 current head `49c5d748c8c9ecc95d21c69a1bd16af0118cba3d` has
   lead-commented docs/status closeout approval but remains unmerged at
   assignment time.
3. task327 produced one large-source `INCLUDED_PASS` (`swe`) and nine
   `BLOCKED_DECONTAM_HIT` large sources. The nine blocked sources must not enter
   packed training data without separate lead-approved false-positive or
   adjudication evidence.
4. task328 does not release task310 training or benchmark evaluation; those
   require accepted packed-contract evidence and later independent review.
5. Lead gate for #391 exact head
   `32e23761dd4d0957f88b2b0705edaa234c6d75bc` accepted the worker report as
   `PARTIAL_PASS_WITH_EXACT_BLOCKERS` / docs-status closeout only. The safe
   carry-forward packed root is the prior constrained task299 seed at
   `/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`.
   `instruction-following-structured`, `agentic-interactive`, and `swe` remain
   raw pass sources blocked before packing due missing accepted split
   exposure/parity and Qwen3-30B supervised-token packing proof. The nine
   task327 decontam-hit sources remain excluded fail-closed.
