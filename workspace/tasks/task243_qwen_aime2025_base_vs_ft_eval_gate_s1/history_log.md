# task243_qwen_aime2025_base_vs_ft_eval_gate_s1 - History Log

<!-- METADATA:SESSION=3 -->

## Session 3 - 2026-06-01 UTC - PR #319 merged and closeout recorded

- Lead approved PR #319 for self-merge if it remained `OPEN/CLEAN`, base `main`, and head `61a12dd8b96e51785a3ece76d5883a419b30dd39`.
- Rechecked PR #319 immediately before merge: base `main`, head `61a12dd8b96e51785a3ece76d5883a419b30dd39`, `mergeStateStatus=CLEAN`, `mergeable=MERGEABLE`, `state=OPEN`.
- Merged PR #319 with GitHub PR merge, not a direct `main` push.
- Merge result: `mergedAt=2026-06-01T16:24:34Z`, merge commit `63415c0617eb7b8ca8c6d12c46405cf8e1a2e571`.
- This is not promotion approval: FT judgment remains blocked until same-harness Qwen3-4B base artifacts exist and FT is compared under the identical corrected AIME2025 protocol.
- Post-merge closeout status recorded on branch `intern_nemotron_worker_3/task243_qwen_aime2025_base_vs_ft_eval_gate_s1_closeout` because the approved #319 head was exact and could not be changed before merge.
- No training, model copy, endpoint launch, live eval, direct main push, or unapproved merge was performed.

## Session 2 - 2026-06-01 UTC - Corrected Qwen3-4B base path

- Lead gate required replacing the old pilot/debug path
  `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507` with the
  coordinator/project-rule path
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Read-only probe confirmed `cephfs_base_path=present` and
  `old_3fs_base_path=missing`.
- Updated `qwen_aime2025_base_vs_ft_gate.yaml`,
  `baseline_protocol_report.md`, status, history, and task knowledge to use
  the `/mnt/cephfs` checkpoint/tokenizer path.
- First same-harness base-score artifact remains blocked only by missing
  corrected AIME input/score-cache visibility and missing reachable Qwen3-4B
  chat endpoint; the base model path itself is no longer a blocker.
- No training, model copy, endpoint launch, live eval, merge, or direct main push was performed.

## Session 1 - 2026-06-01 UTC - Base protocol and gate implementation draft

- Accepted task on branch `intern_nemotron_worker_3/task243_qwen_aime2025_base_vs_ft_eval_gate_s1`.
- Added a focused Qwen AIME2025 base-vs-FT gate module and config draft:
  `qwen_aime2025_base_vs_ft_gate.py` and
  `qwen_aime2025_base_vs_ft_gate.yaml`.
- Added focused tests for required same-harness base score, exact-normalized
  denominator policy, parsed/finish diagnostics, FT-below-base failure, and
  protocol mismatch rejection.
- Added `baseline_protocol_report.md` with Qwen3-4B base checkpoint path, pilot
  smoke protocol, final full protocol, score normalization schema, expected
  artifact paths, and read-only blocker probes.
- Read-only blocker probes found: configured Qwen3-4B base path missing,
  corrected AIME score-cache path missing, and no local chat endpoint listening
  on `127.0.0.1:13000` or `127.0.0.1:30001`.
- Validation run: `PYTHONPATH=src pytest -q tests/recipes/super3/test_qwen_aime2025_base_vs_ft_gate.py` passed with `7 passed`; `PYTHONPATH=src python -m py_compile src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_aime2025_base_vs_ft_gate.py` passed.
- Opened PR #319 to `main`: https://github.com/songCNMS/Nemotron/pull/319.
- No training, model copy, endpoint launch, live eval, merge, or direct main push was performed.

## Session 0 - Assigned

- Created by `intern_nemotron_lead` for `intern_nemotron_worker_3`.
- Initial focus: corrected AIME2025 base-vs-FT non-regression gate and score normalization.
