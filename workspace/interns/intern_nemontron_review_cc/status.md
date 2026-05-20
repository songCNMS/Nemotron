# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task069_wandb_artifact_lineage_publish -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task069_wandb_artifact_lineage_publish |
| PR | pending push |
| Session | 79 |

正在做：task069 Session 1 — W&B artifact lineage publisher。Plan §10
M1 infra deliverable lifted from task021 Session 2 deferral. Session 2
landed the lineage *schema*; this PR lands the *publish* side.

## What's in this PR

### 新 module `milestones/lineage_publisher.py`

Placed sibling to `lineage.py` (scaffold originally said `m1_infra/`
but no such package exists; sibling keeps schema/publish relationship
explicit).

- `WandbArtifactPublisher(wandb_run=None, *, artifact_factory=None)`：
  - `wandb_run=None` → **dry-run** mode (publish 仍返回 PublishResult
    describing what *would* have happened)
  - `artifact_factory` injectable → tests pass `_toy_artifact_factory`
    so no real wandb import needed
  - `publish(record, *, file_root=None, upstream_artifact_resolver=None)`
- `default_upstream_resolver` handles:
  - `manifest` input → reads upstream manifest's lineage block, returns
    `<artifact_name>:latest`
  - `checkpoint` input → `<basename>:latest` heuristic
  - `hf_dataset` / unknown → None (no W&B equivalent)
- `PublishResult` dataclass：dry_run / artifact_name / artifact_type /
  upstream_resolved+unresolved / outputs_attached+missing
- Test doubles (sandbox-runnable, no wandb import):
  - `FakeWandbRun` captures `use_artifact` + `log_artifact` calls
  - `FakeArtifact` captures `add_file` + `metadata` mutations

### `scripts/publish_lineage.py` CLI

Reads `manifest.json`, extracts lineage block, calls publisher. Exit
codes:
- 0: publish OK (or dry-run clean)
- 1: manifest missing
- 2: lineage block missing / malformed
- 3: real publish requested but wandb unavailable

Dry-run path doesn't require wandb installed — useful for CI /
planning. Live publish path lazy-imports wandb so the CLI stays
testable in sandbox.

### Tests (`test_lineage_publisher.py`, 18 cases)

- Dry-run 2: returns PublishResult / still resolves upstream + outputs
- Live mode 5: logs artifact / use_artifact for resolvable inputs /
  skips for unresolvable / each output → add_file / outputs_missing
  surfaced / absolute paths used as-is
- default_upstream_resolver 4: manifest / missing manifest / hf_dataset
  → None / checkpoint heuristic
- Custom resolver 1: overrides default
- Test doubles 2: FakeArtifact captures add_file / FakeWandbRun
  captures in order
- CLI 3: dry-run roundtrip / missing manifest exit 1 / missing lineage
  block exit 2

Sandbox 测试基线 559 → **577 passed + 7 skipped** (18 new)。

## task069 状态

- Session 1 ✓ (this PR) — publisher + CLI + test doubles + dry-run
- Session 2 ☐ — wire publisher into every `prepare_*.py` (M0 / SFT /
  RLVR / SWE1 / SWE2 / RLHF / eval) so each bridge auto-publishes
  after writing manifest.json
- Session 3 ☐ — Cluster verify with real W&B credentials

Roadmap §5b sandbox queue + §1.8 task021 entry 更新。
