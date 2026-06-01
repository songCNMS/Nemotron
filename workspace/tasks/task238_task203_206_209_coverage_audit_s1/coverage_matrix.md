# task238 coverage matrix: task203/task206/task209

<!-- METADATA:STATUS=ReadyForReview,ASSIGNEE=intern_nemotron_worker_3,SESSION=1 -->

## Audit scope

This audit read remote branch/task documentation only. No live endpoint,
training, eval, benchmark, install, Docker, download, model copy, artifact
upload, product-code edit, direct main/master push, or self-merge was
performed.

Worker branch: `intern_nemotron_worker_3/task238_task203_206_209_coverage_audit_s1`

PR: https://github.com/songCNMS/Nemotron/pull/314

## Executive conclusion

| Old task | Old branch head read | Later coverage evidence | Classification | Recovery recommendation |
| --- | --- | --- | --- | --- |
| `task203_qwen_live_sft_train_smoke_s1` | `19ddd0e27bdfb2b9451bb1284e7026e05b74ca5e` | `task216`, `task218`, `task219`, `task220`, and `task224` show the Qwen Stage1 SFT path progressed beyond local dry-run to canonical single-GPU and 8-H200 full-data one-iteration PASS. | Covered by later live validation. | `covered/no recovery` |
| `task206_qwen_sft_train_stack_unblock_probe_s1` | `f9d0610c3e99892c54fb57fe455e455eba4d1c04` | `task209` built the task-owned NemTron train stack, `task216` exercised post-fix train entry, `task218` unblocked causal-conv1d, and `task219`/`task220` proved the resulting stack with live training. | Covered by later live validation and dependency evidence. | `covered/no recovery` |
| `task209_nemtron_h200_sft_live_s1` | `29a3fd586d20e2e046ef20f76939b7118c6125bc` | `task216` verified task215 moved past the task209 packed-sequence blocker, `task218` fixed the new causal-conv blocker, `task219` passed one canonical single-GPU iteration with checkpoint, and `task220` passed one 8-H200 full-data iteration with checkpoint. | Covered by later live validation. | `covered/no recovery` |

No new implementation task is recommended for task203, task206, or task209.
No docs-only recovery is recommended for those old task branches because the
later task216+ chain records stronger, newer evidence for the same train
pipeline decisions. The old remote branches remain readable as historical
evidence, but they do not need to be restored into current `origin/main`.

## Evidence chain read

| Later task | Branch head read | Evidence used in this audit |
| --- | --- | --- |
| `task216_qwen_sft_one_iter_post_task215_live_s1` | `421ccccae237e5aa90ba896f5aba83741b4c0715` | Canonical Qwen one-iteration torchrun after task215/PR #311 reached the training loop and Mamba model forward. It no longer failed on the earlier task209 `packed_seq_params`/Bridge state path; it exposed the next blocker, `MAMBA_SSM_CAUSAL_CONV1D_FWD_FUNCTION_NONE`. |
| `task217_mamba_causal_conv_train_stack_unblock_probe_s1` | `238b5eeb9eac37812d1a4d485ef55e58ccee944f` | Diagnosed task216 as missing `causal-conv1d`/`causal_conv1d_cuda` in the task209 Mamba target, with `causal_conv1d_fwd_function=None`. |
| `task218_causal_conv1d_contained_train_stack_unblock_s1` | `260e849462a93af67afc394dcbf1edc50b3234fa` | Built `causal-conv1d==1.6.2.post1` into task-owned `pip_target`; import/function probes and tiny CUDA extension smoke passed; no train launch by boundary. |
| `task219_qwen_sft_one_iter_post_task218_live_s1` | `9b1a0640d9daca9ab89704ba6ab383e38c6da869` | Canonical single-GPU Qwen-contract one-iteration torchrun passed with `task219_torchrun_rc=0`, iteration `1/1`, loss `1.195105E+01`, skipped/nan `0/0`, and checkpoint saved. |
| `task220_qwen_sft_8gpu_full_data_one_iter_live_s1` | `b761477aef25c944a3deecc452c37958334008d4` | Canonical 8-H200 Qwen3-30B-A3B full-data one-iteration torchrun passed with `task220_torchrun_rc=0`, consumed 8 samples, validation loss recorded, checkpoint saved, and cleanup clean. |
| `task224_qwen_pipeline_live_evidence_matrix_refresh_s1` | `930fb135dc7437ba812377ef444271c10510e952` | Refreshed matrix classifies train-side model/data/H200 availability as PASS through task220. Remaining blockers are benchmark/eval-runner and coverage blockers, not Qwen train pipeline blockers. |
| `task221_qwen_eval_full_benchmark_prepare_s1` | `3e33821d088f0a74eee7e4c64019b204ceb4f6af` | Eval/benchmark preparation only; useful residual-risk context, but not train coverage. |
| `task223_qwen_endpoint_eval_live_after_task220_s1` | `d852588606c5ddef0f183ace503c67749a302d2e` | Endpoint and corrected-math smoke after task220 passed; eval subset/full benchmark held. This is eval-side evidence, not needed to recover old train tasks. |
| `task225_qwen_official_eval_launcher_runtime_unblock_s1` | `2010faf1683e13366e3c662b9d74d225f67f5d74` | Official eval launcher runtime was unblocked for M1 subset discovery. Eval-only context. |
| `task227_qwen_m1_launcher_available_subset_live_s1` | `01b36a9fef71f9fe21caaa8c2a79aeb99526e34b` | Endpoint smoke passed, then task held/cleaned up because evaluator client images were not verified under corrected boundary. Eval-only context. |
| `task230_qwen_official_eval_client_image_unblock_s1` | `c180d863ca52bb766c0cb074c3038d8c9a82c0de` | Found 11 required evaluator client images missing. Eval-only context. |
| `task231_m1_missing_launcher_new_runtime_scan_s1` | `02fa3e68f9a295e47c642a2c3190f58362654349` | Confirmed five M1 targets still lack exact safe launcher mappings. Eval-only context. |
| `task233_qwen_official_eval_client_image_pull_and_subset_live_s1` | `ba6636d1f365d5e94641d675ec3d743ed485d7f7` | Pulled approved eval images; corrected-math official smoke passed; M1 subset partial/held. Eval-only context. |
| `task234_task233_m1_subset_failure_triage_s1` | `595a9dc7b9e4d66bc80d2902ff491c2962732ad7` | Triaged task233 non-pass eval targets. Eval-only context. |

## Per-task coverage assessment

### task203: Qwen local SFT train smoke

Old task evidence read from
`origin/intern_nem_dev_2/task203_qwen_live_sft_train_smoke_s1`:

- Goal was an evidence-only minimal Qwen SFT train smoke through the intended
  Super3 Stage1 SFT entrypoint/profile.
- The `m1_agentic_smoke --dry-run` passed with `rc=0`.
- The resolved config probe passed and resolved the Stage1 SFT train script,
  Qwen profile, packed data path, tokenizer path, checkpoint path, train iters,
  and save interval.
- Focused SFT/Qwen validators passed with `33 passed, 2 skipped`.
- The live one-iteration local smoke was skipped because local prerequisites
  were absent: `torch`, `megatron`, `megatron.bridge`, requested `/mnt/3fs`
  Qwen path, and CUDA availability.

Coverage:

- `task216` used a later merged product commit and the Qwen-contract Stage1 SFT
  path on NemTron, reaching the train loop and a model-forward blocker beyond
  task203 local dry-run scope.
- `task219` passed the canonical single-GPU one-iteration Qwen SFT smoke using
  task209 sample packed data and the corrected task218/task209 train stack.
- `task220` passed the canonical 8-H200 full-data one-iteration Qwen SFT smoke
  with full task208 packed data, validation, checkpoint save, and cleanup.
- `task224` consolidated the train-side live evidence and records remaining
  gaps as eval/benchmark and production-training-scope risks, not as a
  missing minimal Qwen train-smoke proof.

Recommendation: `covered/no recovery`.

Residual risk: task203's exact local workstation one-iteration smoke remains
unproven, but later evidence proves the intended Qwen Stage1 SFT runtime on the
available NemTron/H200 route. The old local `/mnt/3fs` path and missing local
packages are stale environment facts, not current implementation gaps.

### task206: local/project train-stack unblock probe

Old task evidence read from
`origin/intern_nem_dev_2/task206_qwen_sft_train_stack_unblock_probe_s1`:

- Goal was to determine whether any local/project environment could unblock
  task203's one-iteration smoke.
- `/work-agents/.venv/bin/python` had `nemo_run`, but not `torch`,
  `megatron`, or `megatron.bridge`.
- `conda` was not installed; bounded alternate inventory found no other usable
  project venv.
- `nvidia-smi` was not available; requested Qwen model path and fresh task205
  packed splits were absent; fallback task071 packed Qwen splits existed.
- Mandatory `m1_agentic_smoke --dry-run` passed with `rc=0`; focused validators
  passed with `33 passed, 2 skipped`.
- One-iteration local smoke was skipped because prerequisites were missing.
- Task206 handed off to task209 for the supervisor-provided NemTron H200 route.

Coverage:

- `task209` established the NemTron path, staged task208 sample data, created a
  task-owned venv/wheelhouse, and built the task-owned Mamba target.
- `task216` reused the task209 train stack and proved post-task215 code reached
  the next dependency blocker instead of the old packed-sequence path.
- `task218` supplied the missing contained `causal-conv1d` target.
- `task219` and `task220` prove the final composed train stack by passing
  single-GPU and 8-H200 Qwen one-iteration smokes.

Recommendation: `covered/no recovery`.

Residual risk: the task-owned NemTron overlay stack is not a global product
environment. Future reruns must preserve the documented `PYTHONPATH` ordering
and task-owned artifacts. That is operational runbook risk, not a reason to
restore task206 or create a new implementation task.

### task209: NemTron H200 SFT live validation

Old task evidence read from
`origin/intern_nem_dev_2/task209_nemtron_h200_sft_live_s1`:

- Goal was to validate the Super3 Qwen SFT live pipeline beyond local dry-runs
  on the supervisor-provided NemTron H200 node.
- Session 3 staged task208 sample data and verified hashes; direct torchrun
  fallback failed before train start on missing `megatron.energon`.
- Session 4 built a user-owned wheelhouse/venv and cleared several import
  blockers, but canonical one-iteration smoke then failed on missing
  `mamba_ssm`; an attention-only tiny probe reached the training loop and hit
  `packed_seq_params`.
- Session 5 built `mamba_ssm` in a contained target and passed import probes,
  but launch was held by port/process preflight.
- Session 6 canonical single-GPU Qwen-contract run reached model/dataloader
  setup and the training loop, then failed during first forward pass with
  `TypeError: MambaModel.forward() got an unexpected keyword argument
  'packed_seq_params'`; no checkpoint was created.
- Session 7 stopped further live launches and recorded that PM would route a
  product fix task for the packed-sequence blocker.

Coverage:

- `task216` ran after task215/PR #311 on merged commit
  `1d037329f5a02cdc04f2a09a16e7342721be4c87`; the run reached state-aware
  upstream Bridge `gpt_step.forward_step` and model forward, showing the old
  task209 packed-sequence/Bridge-state blocker was no longer the active
  failure.
- `task217` diagnosed the new task216 failure as missing callable
  causal-conv1d functions in the composed Mamba stack.
- `task218` built and verified the contained causal-conv1d package.
- `task219` passed the canonical single-GPU Qwen-contract one-iteration smoke
  and saved a checkpoint.
- `task220` passed the canonical 8-H200 full-data one-iteration smoke,
  validation, checkpoint save, and cleanup.

Recommendation: `covered/no recovery`.

Residual risk: task220 is a one-iteration, random-init distributed smoke
because PM had not supplied a pretrained Megatron checkpoint path. It validates
runtime/data/checkpointing, not full training quality, checkpoint conversion,
serving a trained checkpoint, resume behavior, or production-train duration.
Those are future production-scope decisions, not unfinished task209 recovery.

## Final recommendation

Do not restore task203, task206, or task209 as implementation tasks. Do not
open docs-only recovery tasks for those old branches. The live-validation chain
from task216 through task224 supersedes the old unfinished branch state with
newer evidence, and the remaining active risks belong to future production
training or eval/benchmark planning rather than to the old local/NemTron smoke
tasks.
