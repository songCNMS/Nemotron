# Qwen V4 Hard-Math Recovery Launch - Session 69

## Data Prep

- Local run root: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_recovery_v4`
- M1 train rows: `983397`
- M1 val-shadow rows: `11354`
- Math strategy: `hard_math_recovery_v4`
- Hard verified full-solution rows: source `184551`, written `184551`
- Broad verified full-solution rows: source `360416`, written `90104`
- Final-answer aux rows: source `29`, written `0`
- Format-repair rows: source `321971`, written `0`
- Heldout eval rows: source `1419`, written `1419`

## Packed Artifact

- Packed split path: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_recovery_v4/packed_qwen/splits`
- Total sequences: `1257879`
- Total tokens: `822043015`
- Train rows: `74922`
- Valid rows: `287`
- Train shards: `32`
- Valid shards: `1`
- Chat template: `tokenizer`
- Chat template kwargs: `enable_thinking=false`, `truncate_history_thinking=false`

## Remote Launch

- Remote run root: `/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup/task071_qwen30b_a3b_hard_math_recovery_v4`
- Tmux session: `task067_task071_qwen30b_a3b_hard_math_recovery_v4`
- Train iters: `1874`
- Global batch size: `8`
- GPUs: `0,1,2,3,4,5,6,7`
- Learning rate: `3e-7`
- Min learning rate: `8e-8`
- Warmup iters: `100`
- Eval/save interval: `400`

## Startup Health

- Bridge cache written: `train_4096_train.npy`, `valid_4096_valid.npy`, `packed_4096_metadata.json`
- Latest observed iteration: `160/1874`
- Latest observed lm loss: `0.6407578`
- Skipped iterations: `0`
- NaN iterations: `0`
- GPU state: all 8 H200s active, roughly `81-88G` memory used per GPU during early train loop.

## Local Logs

- Data prep log: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_recovery_v4/local_data_prep_session69.log`
- Sync log: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_recovery_v4/sync_session69.log`
- Launch log: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_recovery_v4/remote_train_launch_session69.log`
- Startup train log copy: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen30b_a3b_hard_math_recovery_v4/metrics/train_session69_startup.log`
