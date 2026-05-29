# task126_benchmark_alignment_source_manifest_path_guard_s1 knowledge

<!-- METADATA:SESSION=2 -->

## Working Notes

- Benchmark alignment evidence has its own `source_manifests` validator; fixes
  here should stay in `benchmark_alignment.py` and avoid Qwen eval repro gate
  files unless the shared contract changes.
- Use raw slash-separated component checks before `Path.resolve()` so
  `..`, `.`, and empty path components cannot be normalized away before the
  policy decision.
- `resolve(strict=True)` plus `relative_to(REPO_ROOT.resolve(strict=True))`
  catches symlinks that point outside the repository while still allowing
  normal repo-relative file paths.
- After PR merge, fast-forward local `main` to the PM-reported merge commit
  before accepting more work, then record closeout on an owned branch.
