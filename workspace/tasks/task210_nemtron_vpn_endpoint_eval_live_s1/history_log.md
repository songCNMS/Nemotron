# History Log

<!-- METADATA:SESSION=5 -->

## Session 1 - 2026-05-30

- Started task210 from `main` at
  `0460c1f0262875fb27ae530d30cd80d805752851`.
- Sent dev_2 coordination request before heavy NemTron GPU serving.
- dev_2 replied not to start heavy Qwen serving yet because task209 owns
  NemTron H200 training/preflight use until release or PM handoff.
- Performed non-heavy NemTron discovery: 8 H200 GPUs visible, Qwen model path
  visible, SGLang 0.5.8 available, vLLM/TensorRT-LLM imports missing.
- Probed vpn: Docker 29.1.3 available but Qwen cephfs model path missing, so
  vpn is staging-only and not a direct model-serving host.
- Did not start a Qwen endpoint and did not run a live request because GPUs were
  not released.
- Reran corrected math dry-run and Qwen/M1/M2 validators; both passed.
- Initially copied evidence artifacts before PM corrected the final artifact
  root.

## Session 2 - 2026-05-30

- Applied PM artifact-root correction and moved final task210 evidence to
  `/mnt/cephfs/data/processing/nemotron-live-validation/task210`.
- Preserved dev_2 coordination blocker: no heavy Qwen serving, endpoint process,
  live chat request, or full benchmark was started while task209 owns H200 GPU
  use.
- Ran `git diff --check` and `git diff --cached --check`; both passed.
- Prepared final docs/status branch for push with corrected artifact paths.

## Session 3 - 2026-05-30

- PM released task210 live continuation after task209 reported NemTron H200 GPUs
  idle and training blocked before start.
- Verified NemTron had no compute apps, no port `13000` listener, and 8 H200s
  idle before launch.
- Started prepared SGLang endpoint command on NemTron with PID `1359959`,
  GPUs `0-7`, port `13000`, and model path
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- SGLang exited before readiness with missing-weight-shard error from the
  NemTron view of the model path.
- Confirmed cleanup state: no server process, no `:13000` listener, no compute
  apps, and all GPUs back idle.
- Did not run live chat smoke, corrected math live eval, launcher-available M1
  subset, or full benchmark because endpoint smoke could not pass.
- Sent PM a blocker report and did not copy, hardlink, download, or stage model
  weights without explicit approval.
- Ran `git diff --check` and `git diff --cached --check`; both passed.

## Session 4 - 2026-05-30

- PM authorized staging the local CPU-visible Qwen model shards into the
  task-owned NemTron-visible path under the corrected task210 artifact root.
- Staged config/tokenizer/index files and all 16 safetensor shards to
  `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/staged_model/Qwen3-30B-A3B-Instruct-2507`.
- Verified staging with `copy_exit=0`, 16 visible shards, matching file-size
  manifest, and matching small-file SHA256 manifest.
- Launched SGLang from the staged model path on 8 H200 GPUs and port `13000`;
  initial direct math smoke showed why the old request schema failed:
  SGLang returned `message.content=null` when Qwen chat template kwargs were
  omitted.
- Applied PM's Session 4 schema correction by sending
  `chat_template_kwargs={enable_thinking:false, truncate_history_thinking:false}`.
- Reran sanitized endpoint smoke with `max_tokens=8`; it passed with HTTP `200`,
  `message.content=OK`, and `reasoning_content=null`.
- Reran direct corrected math live smoke through an artifact-local wrapper that
  injects the same kwargs; AIME and HMMT limit-1 samples both returned non-null
  content, parsed boxed answers, and were correct.
- Did not run the full 27-target benchmark because fresh PM approval is still
  required.
- Stopped SGLang after the smoke runs and verified no port `13000` listener, no
  SGLang processes, and all 8 H200 GPUs idle so task209 can use the node.

## Session 5 - 2026-05-30

- PM reviewed Session 4 artifacts and confirmed staged model, SGLang relaunch,
  corrected endpoint smoke, direct corrected math smoke, and cleanup evidence
  were complete and successful.
- Finalized the evidence-only docs/status/report bookkeeping for the replacement
  branch head.
- Kept full 27-target benchmark held; no full benchmark ran without fresh PM
  approval.
- No additional live endpoint/eval, training, W&B/cluster deploy, artifact
  upload, main/master push, or self-merge was performed during finalization.
