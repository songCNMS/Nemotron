# task152_super3_m1_agentic_docs_path_portability_s1

Status: In progress
Owner: intern_nem_dev_2
Branch: `intern_nem_dev_2/task152_super3_m1_agentic_docs_path_portability_s1`
Base: `17ed7b0e5195878030ff09118fb79caee200b824`
PR: Pending

## Scope

Replace scoped Super3 M1 Agentic SFT docs/config-comment examples that use `/mnt/3fs/data/lei.song/nemotron` with portable `${NEMO_RUN_DIR:-.}/output/super3/...` examples.

Scoped files:

- `src/nemotron/recipes/super3/stage1_sft/config/data_prep/agentic_v0.yaml` comments only
- `src/nemotron/recipes/super3/stage1_sft/README.md`
- `src/nemotron/recipes/super3/milestones/m1_agentic_sft/README.md`
- focused static docs guard under `tests/recipes/super3/`

## Boundaries

Docs/comments/static-test only. Do not touch task150/task151 tiny blend files, production defaults, generated schemas, data-prep logic, training logic, Qwen path examples outside this docs scope, benchmark ledgers, live-run artifacts, or `main`/`master`.
