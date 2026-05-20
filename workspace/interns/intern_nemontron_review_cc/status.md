# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task068_rlhf_toolcall_pairing_harness -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task068_rlhf_toolcall_pairing_harness |
| PR | pending push |
| Session | 89 |

正在做：task068 Session 3 — CLI dispatch + flip RLHF env registry's
tool-call row to active. Final wiring step before cluster smoke (S4).

## What's in this PR

### 新 M0 env `rlhf_toolcall_paired`

- `environment_registry.yaml` 加 env: family `rlhf_preference` /
  verifier `argument_match` / max_turns 1 / sandbox none
- Required fields: `extra_env_info.source_helpsteer2_id` +
  `extra_env_info.source_hermes_id` (audit trail through to upstream
  M0 rows)

### Converter env-name update

Session 2 converter output `environment` field changed from
`single_step_tool_use_with_argument_comparison` (NeMo-Gym name) to
`rlhf_toolcall_paired` (M0 env name). This is so the M1 RLHF bridge's
env_map handles the M0→NeMo-Gym mapping (consistent with other
bridges).

### 新 CLI `scripts/prepare_rlhf_toolcall_pairing.py`

- Args: `--helpsteer2-jsonl`, `--hermes-jsonl`, `--eval-prompts-jsonl`
  (optional), `--output-dir`
- Stream-loads both M0 sources, builds eval-prompt 5-gram set, runs
  the converter, writes `paired.jsonl` + `manifest.json`
- Manifest carries lineage block (`RawDataArtifact` type, both M0
  manifests as inputs, paired.jsonl as output)
- Exit codes: 0 / 1 (missing input) / 2 (malformed JSONL)
- task069 publisher hook called after manifest write (no-op in sandbox)

### RLHF env registry flip

`rlhf_env_registry.yaml`'s `single_step_tool_use_with_argument_comparison`
row：`m0_missing` → **`active`**：
- `m0_env_id: rlhf_toolcall_paired`
- `m0_verifier: argument_match`
- Notes 更新 to reference task068 Session 2/3 deliverables

`RLHF_ENV_MAP` (derived at import time) now contains
`{"rlhf_toolcall_paired": "single_step_tool_use_with_argument_comparison"}`.

### 修 3 个 RLHF bridge today-tests

- `test_rlhf_env_map_empty_today` → flipped to lock active mapping
- `test_coverage_report_today_reflects_main` → counts.active ≥ 1 instead of == 0
- `test_prepare_raises_coverage_aware_error_today` → monkeypatched to
  all-inactive registry (regression guard for the error path; same
  pattern as task016/017/018 Session 2)

### Tests (`test_prepare_rlhf_toolcall_pairing_cli.py`, 11 cases)

- prepare() function 5: writes paired.jsonl + manifest / output uses
  M0 env name / lineage block (2 inputs + 1 output) / eval-prompts
  contamination drops / no eval-prompts passes through
- CLI subprocess 3: smoke roundtrip exits 0 / missing input exits 1 /
  malformed JSONL exits 2
- Registry integration 3: rlhf_env_registry tool-call row is active
  with m0_env_id / m0 env_registry carries rlhf_toolcall_paired /
  RLHF_ENV_MAP picks up new mapping at import

Sandbox 测试基线 651 → **662 passed + 7 skipped** (11 new + 3 modified).

## task068 状态

- Session 1 ✓ (PR #110) — design doc
- Session 2 ✓ (PR #112) — converter implementation
- Session 3 ✓ (this PR) — CLI dispatch + env flip
- Session 4 ☐ — cluster smoke (needs task018 Session 3 judge service +
  end-to-end RLHF pipeline)

Roadmap §5b 更新.
