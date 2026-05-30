# Task Knowledge

<!-- METADATA:SESSION=2 -->

- Required baseline: `0460c1f0262875fb27ae530d30cd80d805752851`.
- Corrected artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task210`.
- Do not use the previous task210 root for new artifacts or final reports; PM
  corrected the task root to the processing path above.
- Local mirror: `/tmp/nemotron-live-validation/task210`.
- NemTron model path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Prepared serving command, not run:
  `CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 python3 -m sglang.launch_server --model-path /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 --served-model-name qwen3-30b-a3b-instruct-2507 --host 0.0.0.0 --port 13000 --tensor-parallel-size 8 --trust-remote-code --context-length 16384 --reasoning-parser qwen3`.
- Stop command if started:
  `pkill -f "sglang.launch_server.*Qwen3-30B-A3B-Instruct-2507"`.
- Summary artifacts:
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task210/task210_evidence_summary.md`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task210/task210_evidence_summary.json`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task210/corrected_artifact_listing.txt`
