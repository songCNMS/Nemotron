# Task Knowledge

<!-- METADATA:SESSION=3 -->

- Task233 corrected-math AIME passed with `max_new_tokens: 8192`,
  `parallelism: 1`, and `limit_samples: 1`; the M1 subset AIME failure used
  `max_new_tokens: 16384`, which exceeded the 16k endpoint context once prompt
  tokens were added.
- GPQA and HLE failures happen before inference because their HF datasets are
  gated and require approved access or an approved mounted cache.
- LiveCodeBench was killed with subprocess return code `137` during
  `release_latest` data/eval work; treat as resource/runtime sizing until a
  reduced smoke or memory profile proves otherwise.
- IFBench fails inside the official evaluator image/runtime import chain
  because `syllapy` imports `pkg_resources`; this is an evaluator runtime gap,
  not an endpoint/model signal.
- RULER requires `config.params.extra.tokenizer` or equivalent tokenizer path;
  the task233 generated command passed `--tokenizer_path "None"`.
- AA-LCR current samples require about 102k-118k input tokens, so the 16k
  endpoint is not a valid release surface for that target without a shorter
  variant/truncation or a larger-context endpoint.
- tau2 and BFCL require external credentials; without them they fail before
  model-quality evidence can be collected.
- `mmlu_prox_chat` had healthy endpoint responses but was killed by cleanup;
  estimate sequential completion at roughly 26-30 hours from observed progress.
- `ns_wmt24pp` was pending at cleanup and never started, so its actual
  runtime/assets are unknown.
- Session 3 added no new target triage findings; it only corrected closeout
  metadata/checklist compliance after the evidence branch was pushed.
