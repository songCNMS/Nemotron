# Task Knowledge

<!-- METADATA:SESSION=5 -->

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
- Session 3 blocker:
  - NemTron sees the Qwen model directory but not the 16
    `model-000xx-of-00016.safetensors` shards required by
    `model.safetensors.index.json`.
  - Local CPU sees the shards at the same path, so the model-path visibility is
    inconsistent across hosts.
  - Do not retry SGLang from that path until the NemTron-visible model shards
    are restored or PM authorizes a specific staging workaround.
- Session 3 artifacts:
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session3/task210_session3_evidence_summary.md`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session3/endpoint_smoke/endpoint_smoke_sanitized.json`
- Session 4 staged model path:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/staged_model/Qwen3-30B-A3B-Instruct-2507`.
- Session 4 serving command uses the staged model path, `--port 13000`,
  `--tensor-parallel-size 8`, and `--reasoning-parser qwen3`.
- Qwen/SGLang schema finding: requests without
  `chat_template_kwargs={enable_thinking:false, truncate_history_thinking:false}`
  can return `message.content=null` with text in reasoning fields, which breaks
  the direct corrected-math parser. Include those kwargs in sanitized smoke and
  direct math smoke requests.
- Corrected Session 4 endpoint smoke artifact:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/endpoint_smoke/session4_chat_smoke_with_kwargs_sanitized.json`.
- Corrected Session 4 direct math smoke artifacts:
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/eval/direct_corrected_math_live_smoke_with_kwargs_command.txt`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/eval/direct_corrected_math_live_smoke_with_kwargs/summary.json`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/eval/direct_corrected_math_live_smoke_with_kwargs/results.jsonl`
- Final Session 4 cleanup artifact:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task210/session4/gpu/final_cleanup_verification_after_with_kwargs.log`.
- Session 5 finalization keeps the full 27-target benchmark held pending fresh
  PM approval; only evidence/status docs were finalized.
