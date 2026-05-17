# task_knowledge

<!-- METADATA:SESSION=2 -->

## 编写规则

- 仅记录跨 session 仍然有用的、且无法通过读代码/git log 直接得出的事实。
- 临时进度放 history_log.md，不要写到这里。

## 知识条目

### M0 health gate 的判定规则

`overall_status(health, baselines)` 现在 fail 的所有情况：
- input_dir 不存在（`build_report` 提前 raise `FileNotFoundError`）。
- `health.environments` 为空。
- 任一 env 的 health summary 非 pass。
- 出现 `unknown_environments`。
- 任一 env 的 oracle aggregate `scored_rows == 0`（一般是 `--skip-code-execution` 把整个 env 都跳过）。
- 任一 env 的 oracle aggregate `pass_at_1 != 1.0`。

只看 markdown / `overall_status` 时记得：oracle baseline 的 1.0 并不是模型质量，只是 wiring。

### hf_val_split fallback

`prepare_m0_assets.prepare_assets` 现在按 dataset spec 是否有 `hf_val_split` 走两条路径：
- 有 → 从 train_split 与 val_split 两个 HF split 各拉满目标行；manifest.datasets 写 `val_holdout: true`。
- 没有（目前只有 Hermes） → 退回旧的"从同一 split 顺序切片"逻辑，并往 `manifest.warnings` 写明"非真正 holdout"；`val_holdout: false`。

补 Hermes 的 val_split 之前需要先选定一个 config（`func_calling_singleturn` 或 `func_calling`），并落到 `hf_val_config`，否则 `hf_dataset` 在多 config 数据集上 `load_dataset` 会失败。
