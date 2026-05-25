# Session 48 Corrected Eval Comparison

## Scope

This comparison uses parser-aligned corrected metrics for original
Qwen3-30B-A3B and the two exported 30B SFT checkpoints:

- Original Qwen3-30B-A3B: fresh Session 47 artifacts under
  `vm4vpn:/tmp/task071_vpn_eval_qwen30b_original_corrected_session47`.
- SFT iter0009119: existing Sessions 35/38 corrected artifacts registered in
  `m1_full_basket_full_non_dry_results_task071_qwen3_30b_a3b_iter0009119.yaml`.
- Conservative iter0010110: existing Sessions 35/38 corrected artifacts
  registered in
  `m1_full_basket_full_non_dry_results_task071_qwen3_30b_a3b_conservative_iter0010110.yaml`.

The current math-final-answer v1 checkpoint stopped at `iter_0005000` is not
included because it has not been exported to HF and served for corrected eval.

## Results

| Model | MMLU-Pro corrected accuracy | Delta vs original | AIME25 corrected accuracy | Delta vs original | HMMT corrected exact % | Delta vs original |
|---|---:|---:|---:|---:|---:|---:|
| Original Qwen3-30B-A3B | 0.5620013298 | 0.0000000000 | 0.5333333333 | 0.0000000000 | 43.3333333333 | 0.0000000000 |
| SFT iter0009119 | 0.5339926862 | -0.0280086436 | 0.0000000000 | -0.5333333333 | 0.0000000000 | -43.3333333333 |
| Conservative iter0010110 | 0.5275930851 | -0.0344082447 | 0.0333333333 | -0.5000000000 | 6.6666666667 | -36.6666666667 |

## Parser Coverage

| Model | MMLU-Pro parsed | AIME25 parsed | HMMT parsed |
|---|---:|---:|---:|
| Original Qwen3-30B-A3B | 1.0000000000 | 0.6500000000 | 0.6666666667 |
| SFT iter0009119 | 1.0000000000 | 0.0333333333 | 0.0333333333 |
| Conservative iter0010110 | 1.0000000000 | 0.9933333333 | 1.0000000000 |

## Interpretation

The corrected comparison still favors the original checkpoint on all three
reasoning metrics. The conservative SFT checkpoint substantially improves
final-answer parser coverage over iter0009119 for AIME/HMMT, but correctness
remains far below the original model. The current math-final-answer v1 strategy
should therefore be evaluated through an exported `iter_0005000` HF checkpoint
before judging whether the sidecar data fixed the correctness gap.

The corrected metrics are diagnostic task071 metrics, not official Qwen
benchmark claims. They are useful for SFT strategy decisions because they remove
the largest legacy harness failures: MMLU-Pro completion truncation and math
final-answer parser mismatch.
