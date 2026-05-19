# task_knowledge

<!-- METADATA:SESSION=2 -->

## Writing Rules

- Record only durable facts that remain useful across sessions.
- Put transient progress in `history_log.md`.

## Knowledge Entries

### PR #51 Validation Follow-Up

`contamination_against` is a `list[str]` contract. It must be enforced in both
M0 runtime validation (`prepare_m0_assets.validate_registries`) and unified-index
schema validation, otherwise malformed registry rows can pass the CI validator
but later produce bad metadata/manifests.
