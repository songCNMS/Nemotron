# task300_qwen_aime_v11_30b_same_harness_testing_s1 - task knowledge

<!-- METADATA:SESSION=3 -->

## Knowledge Entries

1. hard-gate: 30B FT acceptance requires same-harness FT score greater than or
   equal to the exact 30B base score.
2. sequence: base AIME2025 score first, then after training non-AIME canary,
   then corrected AIME2025 FT-vs-base.
3. boundary: AIME2025 is eval/decontam only and cannot enter training.
4. acceptance: worker_3 accepted task300 from `origin/main`
   `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7`; task298 must define the exact
   30B model path and runtime/eval route before base scoring.
5. blocker: task298 has only an acceptance branch at
   `7d24b9295740ef5c21fd443d6399ec9641f8f5c5` with no visible route report or
   artifacts, so task300 must not launch 30B base endpoint/export/eval yet.
6. read-only proof: the candidate 30B model path exists on NemTron and eight
   H200s were idle, but this is not a substitute for task298's required
   runtime/eval route PASS.
7. session2 follow-up: lead explicitly reiterated that 30B base AIME must not
   run until task298 official route PASS is processed; task300 remains blocked
   on that route proof.
8. session3 release: task298/#364 merged with approved route head
   `8f1f7df9d6499eedb150d7e63323df8ee0411f41`; base testing is allowed through
   eval-only SGLang direct from
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
9. session3 base result: corrected same-harness 30B base AIME2025 score is
   `15/30`, exact-normalized accuracy `0.5`, with all-request denominator,
   `30/30` ok, parsed `19/30`, finish reasons `stop=19` and `length=11`.
10. session3 artifact root:
    `/work-agents/intern_nemotron_worker_3/outputs/task300_qwen_aime_v11_30b_same_harness_testing_s1/run_20260602T152008Z`;
    eval directory
    `eval/qwen30b_base_aime2025_30x1_20260602T152351Z`; full completions and
    parser diagnostics are retained as JSONL artifacts.
11. session3 residual: `11/30` length-truncated rows are unparsed and counted
    incorrect under the corrected denominator; future 30B FT comparison must
    use the same cache, prompt, endpoint/chat API semantics, sampling settings,
    parser, normalizer, and denominator.
