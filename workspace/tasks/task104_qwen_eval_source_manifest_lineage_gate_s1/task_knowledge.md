# task104_qwen_eval_source_manifest_lineage_gate_s1 knowledge

<!-- METADATA:SESSION=13 -->

## Working Notes

- `qwen_eval_repro_gate.py` now uses a repo root resolved from
  `Path(__file__).resolve().parents[6]`, matching the file's location under
  `src/nemotron/recipes/super3/milestones/m1_eval_basket`.
- Source manifest validation mirrors the benchmark alignment ledger posture:
  absolute paths are rejected, and repo-relative paths must point to existing
  files under the repository root.
- The focused tests intentionally do not depend on loading local raw artifacts,
  so source-manifest lineage validation remains covered even when production
  raw artifact paths are unavailable in a clean sandbox.
