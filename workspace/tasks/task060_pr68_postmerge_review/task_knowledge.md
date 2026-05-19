# task_knowledge

<!-- METADATA:SESSION=1 -->

## Writing Rules

- Record only durable facts that remain useful across sessions.
- Put transient progress in `history_log.md`.

## Knowledge Entries

### Contamination Audit Sentinel Matching

`is_placeholder_entry()` should not use arbitrary substring matching. Use exact
or delimiter-aware prefix matching so placeholder notes such as `TBD: AIME`
still count while real hyphenated eval names such as `Pending-Eval-2026` do not.
