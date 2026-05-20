# task_knowledge

<!-- METADATA:SESSION=2 -->

## Writing Rules

- Record only durable facts that remain useful across sessions.
- Put transient progress in `history_log.md`.

## Knowledge Entries

- `revision_audit.is_pinned()` must reject human placeholders such as `TBD`; otherwise M0 production registry rows can pass CI but fail `datasets.load_dataset(..., revision="TBD")` at runtime.
- Pinned `SWE-Gym/SWE-Gym-Lite` revision `f70b1a29ab120eb0a0ee7a1deb029825e735b2b0` has only a `train` split and patch-style rows (`problem_statement`, `patch`, tests), not `messages` trajectories.
- Pinned `nvidia/HelpSteer2` revision `990b2711a36180dd19d9c94b8627844866f8982a` default config has scalar response-rating rows (`prompt`, `response`, `helpfulness`, `coherence`, `correctness`, `complexity`, `verbosity`). Adjacent same-prompt rows can be paired for GenRM comparison data.
