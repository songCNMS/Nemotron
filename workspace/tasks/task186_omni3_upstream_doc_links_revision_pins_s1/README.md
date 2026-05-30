# task186_omni3_upstream_doc_links_revision_pins_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

Status: In progress
Owner: intern_nem_dev_2
Branch: `intern_nem_dev_2/task186_omni3_upstream_doc_links_revision_pins_s1`
Base: `a655174376be9b1880fc9b756cc37af76590f747`
Original assignment base: `c76c51dba5e8796d7b7f12c25fcd172f4c9c8bfa`
PR: https://github.com/songCNMS/Nemotron/pull/293

## Summary

Pin mutable Omni3 upstream GitHub documentation links to exact upstream commits
so docs references do not drift while preserving branch names in visible prose.

## Scope

- `docs/nemotron/omni3/README.md`
- `docs/nemotron/omni3/architecture.md`
- `docs/nemotron/omni3/sft.md`
- `docs/nemotron/omni3/rl.md`
- `src/nemotron/recipes/omni3/stage0_sft/README.md`
- `src/nemotron/recipes/omni3/stage1_rl/README.md`
- Focused static tests under `tests/docs/`
- Task/status/report bookkeeping for `intern_nem_dev_2`

## Pins

- Megatron-Bridge `nemotron_3_omni` links:
  `648756cb99eed872d9e577243495840b9395a6f7`
- NeMo-RL `nano-v3-omni` links:
  `98ba11c0a77e177a903cd3756570684437a08e8d`

## Boundaries

- Static docs/tests only.
- No live git clone/fetch/checkout, build, download, recipe execution, data
  prep, train/eval, endpoint, W&B, cluster, deploy, artifact operation, direct
  `main`/`master` push, or self-merge.

## Acceptance Checks

- PASS: `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/docs/test_omni3_upstream_doc_links_revision_pins.py` (1 passed)
- PASS: `/work-agents/.venv/bin/python -m py_compile tests/docs/test_omni3_upstream_doc_links_revision_pins.py`
- PASS: `/work-agents/.venv/bin/ruff check tests/docs/test_omni3_upstream_doc_links_revision_pins.py`
- PASS: structured static probe for scoped branch-link removal, exact SHA links, and preserved branch context prose
- PASS: scoped stale mutable upstream grep over Omni3 docs/recipe READMEs
- PASS: added-line live-surface scan; hits are static GitHub URL pins, static tests, and task/status docs only
- PASS: `git diff --check`
- PASS: `git diff --cached --check`
