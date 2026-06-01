# Task Knowledge

<!-- METADATA:SESSION=2 -->

- Task233 was authorized to pull only these 11 refs, all at tag `26.03`:
  `nvcr.io/nvidia/eval-factory/aa-lcr`,
  `nvcr.io/nvidia/eval-factory/bfcl`,
  `nvcr.io/nvidia/eval-factory/hle`,
  `nvcr.io/nvidia/eval-factory/ifbench`,
  `nvcr.io/nvidia/eval-factory/livecodebench`,
  `nvcr.io/nvidia/eval-factory/lm-evaluation-harness`,
  `nvcr.io/nvidia/eval-factory/long-context-eval`,
  `nvcr.io/nvidia/eval-factory/nemo-skills`,
  `nvcr.io/nvidia/eval-factory/scicode`,
  `nvcr.io/nvidia/eval-factory/simple-evals`, and
  `nvcr.io/nvidia/eval-factory/tau2-bench`.
- VPN did not directly reach NemTron `10.100.2.62:13000`; the bounded SSH
  reverse tunnel exposed the existing task233 SGLang endpoint as
  `127.0.0.1:13128` on VPN and worked for endpoint health, model listing, and
  evaluator client calls.
- With `deployment.type=none`, `nemo-evaluator-launcher` did not start a
  deployment/server container. Client containers used `--network host` so the
  VPN host tunnel was reachable.
- `lm-evaluation-harness.mmlu_pro` was the only completed M1 subset target
  using the completions path and passed.
- Corrected-math smoke passed for `simple_evals.AIME_2025` and
  `nemo_skills.ns_hmmt_feb2025`, but the M1 subset variant of
  `simple_evals.AIME_2025` failed with HTTP 400 route/client behavior.
- M1 subset failures observed before cleanup included gated HF datasets,
  missing evaluator runtime dependency `pkg_resources`, missing tokenizer path,
  context length greater than the 16k endpoint context, missing API keys, and
  external API/auth errors.
- `mmlu_prox_chat` is long-running in this launcher shape. At the cleanup
  decision it was still partial at about `10420/11759`; `ns_wmt24pp` had not
  started useful work.
- Task233 cleanup must target only task233-owned resources: evaluator
  invocation `5e3f10e5af8917d7`, tunnel socket
  `/tmp/task233_vpn_reverse_tunnel_mux.sock`, VPN port `13128`, and SGLang
  process tree rooted at NemTron PID `2354311`.
- The unrelated `:8000` listener existed before cleanup, was documented only,
  and was left untouched.
