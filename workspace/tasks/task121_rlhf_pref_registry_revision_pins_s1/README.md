# task121_rlhf_pref_registry_revision_pins_s1 - RLHF pref registry revision pins

<!-- METADATA:STATUS=Working,ASSIGNEE=intern_nem_dev_2,SESSION=17 -->

## Background

The M1 RLHF preference-data registry marked three candidate Hugging Face
datasets as requiring revision pins but left `hf_revision` unset. The
revision audit therefore emitted informational findings instead of a clean
source-lineage report.

## Goals

- Pin HelpSteer2, UltraFeedback, and distilabel Orca DPO pair registry rows to
  current Hugging Face dataset commit SHAs.
- Preserve `hf_revision_pin_required: true`, source URLs, licenses,
  contamination notes, and candidate/active semantics.
- Update revision-audit tests so live RLHF pref candidates are no longer
  unpinned informational findings.
- Keep synthetic unpinned required pref fixtures informational.

## Metadata Probe

- `nvidia/HelpSteer2`: `990b2711a36180dd19d9c94b8627844866f8982a`
- `openbmb/UltraFeedback`: `40b436560ca83a8dba36114c22ab3c66e43f6d5e`
- `argilla/distilabel-intel-orca-dpo-pairs`:
  `0b10ec0df32c919f95126b203c8f5962b6875896`

## Out Of Scope

- Dataset downloads, data prep, train/eval, endpoint calls, W&B, cluster jobs,
  deployment, direct `main` or `master` push, and self-merge.

## Acceptance Criteria

- [x] Branch created from `origin/main`
  `8e703277627132ee5277a1027034154d3726f163`.
- [x] All three RLHF pref candidates carry pinned `hf_revision` values.
- [x] Live revision-pin audit has no pref informational findings.
- [x] Synthetic required pref candidates without pins remain informational.
- [x] Focused pytest, registry validator, py_compile, Ruff, and diff
  whitespace checks pass.
- [x] PR opened to `main`.

## PR

- https://github.com/songCNMS/Nemotron/pull/228
