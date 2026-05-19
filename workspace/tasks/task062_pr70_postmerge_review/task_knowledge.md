# task_knowledge

<!-- METADATA:SESSION=2 -->

## Writing Rules

- Record only durable facts that remain useful across sessions.
- Put transient progress in `history_log.md`.

## Knowledge Entries

### Eval Result Loader Contract

`load_eval_results()` should reject malformed NeMo Evaluator JSON before
`diff_eval_runs()` sees it; in particular, top-level `tasks` must be a mapping.
