# task125_qwen_eval_source_manifest_path_escape_guard_s1 knowledge

<!-- METADATA:SESSION=22 -->

## Working Notes

- `PurePosixPath` normalizes `a//b` and `a/./b`, so the helper checks raw
  slash-separated components before joining paths under `REPO_ROOT`.
- `Path.resolve(strict=True)` is still used to prove the target exists and to
  detect symlink escapes outside the repository.
- The source-manifest helper now rejects directories after resolving the final
  target, preserving clear missing-file versus non-file messages.
