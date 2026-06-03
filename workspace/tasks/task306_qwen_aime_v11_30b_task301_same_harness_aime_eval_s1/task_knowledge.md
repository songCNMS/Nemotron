# task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1 - task knowledge

<!-- METADATA:SESSION=5 -->

## Knowledge Entries

1. Accepted 30B base comparator is task300: Qwen3-30B-A3B corrected AIME2025
   score `15/30 = 0.5`.
2. task300 base artifact root:
   `/work-agents/intern_nemotron_worker_3/outputs/task300_qwen_aime_v11_30b_same_harness_testing_s1/run_20260602T152008Z`.
3. Candidate FT checkpoint is task301 salvage checkpoint
   `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints/iter_0000035`.
4. task301 is not a clean training PASS: it reached `35/35`, saved the
   checkpoint, skipped `0`, NaN `0`, then built-in validation hung and
   `train_rc=1`.
5. task304/task305 accepted only a synthetic non-AIME checkpoint-load/completion
   canary with residuals. They are not corrected AIME evidence and do not
   authorize promotion/export/endpoint/additional training.
6. task306 PASS requires FT exact-normalized corrected AIME2025 score
   `>= 15/30` under the same corrected protocol as task300.
7. AIME2025 prompts and labels are held-out eval/decontam inputs only and must
   not enter trainable data.
8. If task306 cannot prove prompt/cache/generation/parser/normalizer/denominator
   equivalence to task300, it must report HOLD or a justified no-training base
   rerun instead of judging the FT checkpoint.
9. task306 completed the no-export/no-endpoint corrected AIME2025 30x1
   evaluation for task301 `iter_0000035` at run root
   `/work-agents/intern_nemotron_worker_3/outputs/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_20260602T190432Z`.
10. Final task306 disposition is `FAIL`: FT `14/30 = 0.4666666666666667`,
    below accepted task300 base `15/30 = 0.5`.
11. Result artifacts retained `30/30` results, full completions, and parser
    diagnostics; parsed rows `17/30`; finish reasons `stop=17`, `length=13`.
12. Same-harness proof was complete except for the explicit route residual:
    `sampling_exact_parameter_match=false` because task306 used the accepted
    no-export MCore greedy substitute while task300 base used SGLang endpoint
    transport.
