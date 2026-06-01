# task243_qwen_aime2025_base_vs_ft_eval_gate_s1 - History Log

<!-- METADATA:SESSION=1 -->

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
- No training, model copy, endpoint launch, live eval, merge, or direct main push was performed.

## Session 0 - Assigned

- Created by `intern_nemotron_lead` for `intern_nemotron_worker_3`.
- Initial focus: corrected AIME2025 base-vs-FT non-regression gate and score normalization.
