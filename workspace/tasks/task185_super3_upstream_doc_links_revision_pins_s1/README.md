# task185_super3_upstream_doc_links_revision_pins_s1

<!-- METADATA:STATUS=Complete,ASSIGNEE=intern_nem_dev_1,SESSION=3 -->

## Scope

- Pin Super3 docs and recipe README upstream GitHub doc links from mutable
  `blob/super-v3` URLs to exact upstream revisions.
- Megatron-Bridge Super3 doc links pin to
  `f570c0529c81b57cb2ae909bd31a19408c7f4583`.
- NeMo-RL Super3 guide links pin to
  `bb0a7d43931950a74522e159f7117543a87b580b`.
- Preserve branch-context prose and existing exact checkout snippets.
- Add focused static coverage under `tests/docs/`.

## Boundaries

- Static docs/tests/status only.
- No live git clone/fetch/checkout, build, download, recipe execution, data
  prep, train/eval, endpoint, W&B, cluster, deploy, artifact operations,
  direct `main`/`master` push, or self-merge.

## Status

- Base: `f74e7c05668f96766d10c730fcd14ddec7191350`
- Branch: `intern_nem_dev_1/task185_super3_upstream_doc_links_revision_pins_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/292
- Merge SHA: `a655174376be9b1880fc9b756cc37af76590f747`
- Final PR head: `db13cd97ed91cbf2b068f96d6ebcac407250bf38`
- Validated implementation head: `a832efc15a9e22e745febb96c5f4e8bf6cc9e9f5`
- Checks: focused docs revision-pin pytest, py_compile, Ruff, structured
  static probe, scoped stale-link grep, added-line live-surface scan,
  `git diff --check`, and `git diff --cached --check` passed.
- Merged-main verification: PR #292 was squash-merged and verified on main
  `a655174376be9b1880fc9b756cc37af76590f747`.
