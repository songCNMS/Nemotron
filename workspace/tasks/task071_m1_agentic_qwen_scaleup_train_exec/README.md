# task071_m1_agentic_qwen_scaleup_train_exec

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemontron_code_reading -->

## Background

PR #93 merged the reusable Qwen M1 Agentic SFT scale-up planner. The next step is to execute the formal scale-up path from latest `main`: generate scripts, prepare packed data locally, sync artifacts to NemTron, launch Qwen training, and validate the eval entry.

## Goals

- Regenerate formal scale-up scripts from latest `main`.
- Run local M0 -> M1 Agentic SFT -> Qwen packed data prep.
- Sync code and artifacts to NemTron.
- Launch remote Qwen3 4B M1 Agentic SFT training in tmux.
- Run the configured eval dry-run entry and record how to run the full eval once a checkpoint is ready.

## Acceptance

- [ ] Formal scripts and manifest are generated under `../outputs/task071_qwen_scaleup_train_exec`.
- [ ] Local data prep completes and produces M1 Agentic SFT JSONL plus Qwen packed split artifacts.
- [ ] Artifacts are synced to NemTron.
- [ ] Remote training tmux session is launched and log path is recorded.
- [ ] Eval dry-run validates the selected basket config.
