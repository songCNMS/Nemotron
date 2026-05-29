# task123_omni3_rl_source_revision_pins_s1 - Omni3 RL source revision pins

<!-- METADATA:STATUS=Working,ASSIGNEE=intern_nem_dev_2,SESSION=19 -->

## Background

Omni3 Stage1 RL data-prep configs referenced Hugging Face sources with
floating refs, and the RL-Omni download/cache path did not include source
revision identity. A changed upstream dataset could therefore reuse an
existing prepared-run cache or omit source lineage.

## Goals

- Pin MPO, Vision, and Text Omni3 Stage1 RL Hugging Face sources to current
  dataset commit SHAs.
- Pass the MPO/Vision `source_revision` through to `snapshot_download()`.
- Include `source_uri` and `source_revision` in RL-Omni run hash/config
  identity.
- Record MPO/Vision source identity in artifact fields and metadata.
- Preserve backward-compatible `DataBlend` loading while allowing text blend
  datasets to carry a revision pin.
- Fail Omni3 text data-prep when `source_revision` is configured but
  `source_uri` has no matching dataset row in the blend.

## Metadata Probe

- `OpenGVLab/MMPR`: `fe3f35704dcfc2709a072b07df0ecab6046b2c0c`
- `OpenGVLab/MMPR-Tiny`: `eb493212c9614b69ca49cd6e66719413c514459b`
- `nvidia/Nemotron-3-Nano-RL-Training-Blend`:
  `ffd169f2b74bb492ec607d64bd56f7435054972b`

## Out Of Scope

- Dataset downloads, live data prep, train/eval, endpoint calls, W&B, cluster
  jobs, deployment, direct `main` or `master` push, and self-merge.

## Acceptance Criteria

- [x] Branch created from `origin/main`
  `dc6e00e741c4189051bc4db4052283dbc78d0c13`.
- [x] MPO, Vision, and Text data-prep configs carry explicit 40-char lowercase
  SHA revision pins.
- [x] RL-Omni downloads receive configured `source_revision`.
- [x] RL-Omni run hash/config identity includes source URI and revision.
- [x] MPO/Vision artifacts record pinned source identity.
- [x] Text blend revision plumbing remains backward-compatible.
- [x] Text data-prep rejects pinned source revisions without a matching blend
  dataset row.
- [x] Focused pytest, py_compile, Ruff, metadata probe, static source-pin
  probe, and diff whitespace checks pass.
- [ ] PR opened to `main`.

## PR

- Pending.
