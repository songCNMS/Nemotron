# task114_mmpr_zip_extraction_traversal_guard_s1 knowledge

<!-- METADATA:SESSION=15 -->

## Working Notes

- Validate the complete archive member list before extracting any file; this
  prevents a mixed archive from writing safe-looking members before failing on
  a later traversal member.
- Treat backslashes as path separators during validation so Windows-style
  traversal is rejected on POSIX hosts too.
- Drive-letter paths such as `C:/tmp/file` are unsafe even when they are not
  absolute on the current host.
- The VLM stage can use whole-archive guarded extraction, while the scripts
  keep per-member extraction to preserve their existing tqdm progress bars.
