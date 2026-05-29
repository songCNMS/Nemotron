# task122_omni3_valor_tar_extraction_guard_s1

## Scope

- Replace Omni3 Valor32k direct `tar xf` extraction with a guarded Python tar
  extraction path in `stage0_sft/data_prep.py`.
- Preserve `strip_components=4` behavior for canonical
  `raid/datasets/audioset/valor_videos/*.mp4` entries.
- Reject absolute paths, `..` traversal, members that strip to empty names,
  symlinks, hardlinks, special entries, and extraction targets escaping
  `videos_dir`.
- Add focused synthetic tar tests.

## Boundaries

- No live Valor32k download/data prep, HF download, training, eval, endpoint,
  W&B, cluster job, deployment, direct `main`/`master` push, or self-merge.

## Status

- Branch: `intern_nem_dev_3/task122_omni3_valor_tar_extraction_guard_s1`
- Base: `190e8c53c59c08696348b1ae7ca7b58ac4fc8633`
- PR: https://github.com/songCNMS/Nemotron/pull/229
