# task067_m1_agentic_qwen_scaleup - task_knowledge

<!-- METADATA:SESSION=1 -->

## Notes

- task066 证明 Qwen3 4B M1 Agentic SFT smoke 可在 NemTron GPUs 0/1 上以 TP=2 完成。
- NemTron 缺 `cosmos_xenna`，所以 packed data prep 仍应在本地 `/work-agents/.venv` 完成后同步 artifacts。
- M1 Agentic SFT scale-up data allowlist should use exactly the 11 builder-supported M0 dataset ids; SWE1/SWE2/RLHF rows are separate milestones and should not be passed into `prepare_m1_agentic_sft.py`.
- A reusable scale-up plan should derive `TRAIN_ITERS` from `training_manifest.json` on NemTron instead of hardcoding it into the remote launch script.
- When launching the actual training inside tmux, `TRAIN_ITERS` must be exported; otherwise the tmux child shell can expand it as an empty value.
