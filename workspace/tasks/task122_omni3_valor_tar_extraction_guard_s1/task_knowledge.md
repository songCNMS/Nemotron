# task122_omni3_valor_tar_extraction_guard_s1 knowledge

<!-- METADATA:SESSION=22 -->

## Working Notes

- `_extract_valor32k_tar()` now opens the source tar with Python `tarfile` and
  delegates to `_extract_guarded_tar_members()`.
- The guard computes stripped targets before extraction and rejects unsafe
  member types or paths before any member is written.
- Existing post-extraction MP4 layout checks remain in place after guarded
  extraction.
- Session 21 added no implementation change; it recorded PR #229 readiness and
  status/report evidence.
- Session 22 added no new implementation knowledge. PR #229 is merged at
  `dc6e00e741c4189051bc4db4052283dbc78d0c13`.
