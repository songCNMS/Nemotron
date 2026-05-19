# intern_nemontron_code_reading - personal knowledge base

<!-- METADATA:SESSION=6 -->

---

## Knowledge entries

### Task005 Qwen full-loop validation

For M1 Agentic SFT on `NemTron`, use `/root/nemotron_session5_venv/bin/python` with `PYTHONPATH=$PWD/src`, Qwen3-4B-Instruct-2507 model/tokenizer at `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`, and pretrained Bridge checkpoint `/mnt/3fs/data/lei.song/nemotron/checkpoints/qwen3-4b-instruct-2507-megatron-bridge-20260517a`. Eval-only runs still need nonzero scheduler steps; `train.train_iters=1 scheduler.lr_decay_iters=1 scheduler.lr_warmup_iters=0 train.skip_train=true` is the stable override.

### Live HF checks in PR tests

Keep live Hugging Face `dataset_info()` checks behind an explicit env gate such as `NEMOTRON_RUN_LIVE_HF_TESTS=1`; default PR tests should assert static slugs/subsets and avoid network-dependent skip/fail behavior.

### M0 Contamination Metadata Validation

`contamination_against` is a `list[str]` contract. Enforce it both in M0 runtime registry validation and unified-index schema validation so malformed rows fail before metadata/manifests are emitted.

### Contamination Audit Sentinel Matching

Placeholder sentinel detection for contamination audits should use exact or delimiter-aware prefix matching, not arbitrary substring matching. `TBD: AIME` should count as a placeholder note, while real hyphenated eval names such as `Pending-Eval-2026` or `TBD-Eval-2026` should not be flagged.

### Task History Session Metadata

When a task history log appends a later session, advance the `METADATA:SESSION` header to the latest session number so machine-readable task state does not lag behind the human-readable log.

### Eval Result Loader Contract

`load_eval_results()` should reject malformed NeMo Evaluator JSON before `diff_eval_runs()` sees it; top-level `tasks` must be a mapping, not merely a present key.

### Intern Status Metadata

Idle intern status metadata should keep an explicit empty task field: `METADATA:STATUS=Idle,TASK=`.

### Task File Session Metadata

Every task `history_log.md` and `task_knowledge.md` should carry a `METADATA:SESSION=<latest>` header near the top, matching the latest session recorded in that file.
