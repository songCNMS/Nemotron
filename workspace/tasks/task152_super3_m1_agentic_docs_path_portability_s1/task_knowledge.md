<!-- METADATA:SESSION=2 -->

# Task Knowledge

- Scope is docs/comments/static-test only.
- Do not touch task150/task151 tiny blend files.
- The scoped named-user path to eliminate is `/mnt/3fs/data/lei.song/nemotron`.
- Portable examples use `${NEMO_RUN_DIR:-.}/output/super3/...` so shell snippets remain copyable without a named-user mount.
- PR #259 was squash-merged to `main` at `bc717911b917fbab63f785163da75773effc4872`; PM verified merged-main docs checks without live M0/M1 data prep, SFT packing, train/eval, endpoint, W&B, cluster, deploy, or artifact download actions.
