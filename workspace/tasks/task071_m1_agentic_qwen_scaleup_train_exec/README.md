# task071_m1_agentic_qwen_scaleup_train_exec

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemontron_code_reading -->

## Background

PR #93 merged the reusable Qwen M1 Agentic SFT scale-up planner. The next step is to execute the formal scale-up path from latest `main`: generate scripts, prepare packed data locally, sync artifacts to NemTron, launch Qwen training, and validate the eval entry.

## Goals

- Regenerate formal scale-up scripts from latest `main`.
- Run local M0 -> M1 Agentic SFT -> Qwen packed data prep.
- Sync code and artifacts to NemTron.
- Launch remote Qwen3 4B M1 Agentic SFT training in tmux.
- Run the configured eval dry-run entry and record how to run the full eval once a checkpoint is ready.

## Acceptance

- [x] Formal scripts and manifest are generated under `../outputs/task071_qwen_scaleup_train_exec`.
- [x] Local data prep completes and produces M1 Agentic SFT JSONL plus Qwen packed split artifacts.
- [x] Artifacts are synced to NemTron.
- [x] Remote training tmux session is launched and log path is recorded.
- [x] Eval dry-run validates the selected basket config.

## Results

- Local output root: `/work-agents/intern_nemontron_code_reading/outputs/task071_qwen_scaleup_train_exec`.
- Remote output root: `/work-agents/intern_nemontron_code_reading/task071_qwen_scaleup_train_exec/task071_qwen_scaleup_train_exec`.
- Data scale: 11 M0 slices, M1 train rows 1100, M1 val shadow rows 273.
- Packed artifacts: 32 shards, 944,050 tokens, 244 train packed rows, 8 valid packed rows.
- Training: Qwen3 4B TP=2 on NemTron GPUs 0/1, global batch size 2, train_iters 122.
- Final validation: iteration 122, loss `2.835580E-01`, PPL `1.327846E+00`.
- Final checkpoint: `/work-agents/intern_nemontron_code_reading/task071_qwen_scaleup_train_exec/task071_qwen_scaleup_train_exec/checkpoints/iter_0000122`.
- Eval entry: `m1_full_basket` dry-run passed after training.
