# task039_m2_eval_basket - task_knowledge

<!-- METADATA:SESSION=3 -->

## Session 1 Notes

- Reuse `eval_basket_registry` for M2 rows; avoid adding a new
  unified-index schema kind unless a future session needs stricter
  generic validation.
- Keep M2 live-runtime blockers in row metadata rather than pretending benchmark rows are sandbox-ready.
- The Session 1 adapter config is a dry-run/config-validation scaffold.
  Live NeMo Evaluator tasks, benchmark assets, and baseline numbers are
  cluster-bound.
- Session 2 added no implementation knowledge; it confirmed post-merge sync and Idle status.
- Session 3 keeps 122B-class parity as sandbox threshold config only.
  Frozen production baseline values are not encoded; callers must provide
  local score maps when evaluating gaps.
