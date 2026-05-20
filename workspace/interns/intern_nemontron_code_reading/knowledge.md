# intern_nemontron_code_reading - personal knowledge base

<!-- METADATA:SESSION=7 -->

---

## Knowledge entries

### Task005 Qwen full-loop validation

For M1 Agentic SFT on `NemTron`, use `/root/nemotron_session5_venv/bin/python` with `PYTHONPATH=$PWD/src`, Qwen3-4B-Instruct-2507 model/tokenizer at `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`, and pretrained Bridge checkpoint `/mnt/3fs/data/lei.song/nemotron/checkpoints/qwen3-4b-instruct-2507-megatron-bridge-20260517a`. Eval-only runs still need nonzero scheduler steps; `train.train_iters=1 scheduler.lr_decay_iters=1 scheduler.lr_warmup_iters=0 train.skip_train=true` is the stable override.

### Task066 Qwen local runtime delta

On 2026-05-20 in this workspace, `/root/nemotron_session5_venv/bin/python` no longer exists. `/work-agents/.venv` can run M0/M1 Agentic SFT data prep and Qwen tokenizer packed artifacts because it has `datasets`, `transformers`, `pyarrow`, and `cosmos_xenna`; it cannot launch Qwen SFT because it lacks `torch` and `megatron.bridge`, and the host has no visible NVIDIA GPU.

### Task066 NemTron Qwen SFT run

NemTron host `lg-cmc-b7r202-e09u26-h200-000459` has 8x H200 and `/root/nemotron_session5_venv` with `torch`/`megatron.bridge`, but no `cosmos_xenna`. For task066 Session 2, sync code/artifacts via `tar | ssh tar` because GitHub 443 was unreachable from NemTron. Final Qwen3 4B M1 Agentic SFT smoke used GPUs 0/1, TP=2, 13 iterations, final validation loss `3.309570E-01`, PPL `1.392300E+00`, and saved checkpoint `/work-agents/intern_nemontron_code_reading/outputs/task066_qwen_sft/checkpoints/iter_0000013`.

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

### Task065 HF Data Registry Review

`revision_audit.is_pinned()` must reject human placeholders such as `TBD`; otherwise M0 production registry rows can pass CI but fail `datasets.load_dataset(..., revision="TBD")` at runtime.

Pinned `SWE-Gym/SWE-Gym-Lite` revision `f70b1a29ab120eb0a0ee7a1deb029825e735b2b0` has only a `train` split and patch-style rows (`problem_statement`, `patch`, tests), not `messages` trajectories.

Pinned `nvidia/HelpSteer2` revision `990b2711a36180dd19d9c94b8627844866f8982a` default config has scalar response-rating rows (`prompt`, `response`, `helpfulness`, `coherence`, `correctness`, `complexity`, `verbosity`); adjacent same-prompt rows can be paired for GenRM comparison data.
