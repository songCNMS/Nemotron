# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 80 |

刚做完：task069 Session 1 — W&B artifact lineage publisher + CLI
(PR #104 / 860e175, merged 2026-05-19).

- 新 module `milestones/lineage_publisher.py` (sibling to `lineage.py`):
  - `WandbArtifactPublisher(wandb_run=None, *, artifact_factory=None)` —
    injectable W&B run + artifact factory; dry-run mode when wandb_run=None
  - `default_upstream_resolver`: manifest → upstream artifact_name;
    checkpoint → basename heuristic; hf_dataset/unknown → None
  - `PublishResult` dataclass surfaces dry_run / artifact_name+type /
    upstream_resolved+unresolved / outputs_attached+missing
  - `FakeWandbRun` + `FakeArtifact` test doubles (no wandb import needed)
- 新 CLI `scripts/publish_lineage.py` — exit codes 0/1/2/3; dry-run
  needs no wandb install; live publish lazy-imports
- 18 个新 pytest case; sandbox 测试基线 559 → 577 passed + 7 skipped
- Closes M1 infra W&B publish gap deferred since task021 Session 2

## 本轮 PRs 收尾 (Roadmap refresh sprint complete)

- PR #94 — roadmap refresh + 4 gap-task scaffolds
- PR #95 — task067 → task070 rename (ID collision)
- PR #97 — task013 Session 2a (two-stage SFT driver + YAMLs)
- PR #99 — task040 Session 1 (W1 curriculum sampler)
- PR #101 — task070 Session 1 (OpenHands wrapper Protocol + fake)
- PR #104 — task069 Session 1 (W&B lineage publisher + CLI)

Sandbox 测试基线 progression: 506 → 520 → 543 → 559 → 577 passed
(共 4 sandbox sessions + roadmap refresh = 71 new tests across the sprint).

## task069 状态

- Session 1 ✓ (this PR)
- Session 2 ☐ — wire `lineage_publisher.publish()` into every
  `prepare_*.py` (M0 / SFT / RLVR / SWE1 / SWE2 / RLHF / eval)
- Session 3 ☐ — Cluster verify with real W&B credentials

## 下一候选 (sandbox-runnable per roadmap §5b)

- task040 Session 2 — wire sampler into prepare_m0_assets.py /
  prepare_m1_agentic_sft.py via `--curriculum-policy` CLI flag
- task057 Session 1 — M0 tier2 expansion (lights up RLVR2/RLVR3 active)
- task068 Session 1 — RLHF tool-call pairing harness design doc
- task069 Session 2 — wire publisher into every prepare_*.py (natural
  follow-on)

Cluster-bound queue (waiting on NemTron access)：task013 Session 2b /
task014 Session 2 cluster part / task016 Session 3 / task017 Session 3 /
task018 Sessions 3-4 / task019 Sessions 2-3 / task020 Session 3 /
task021 Session 4 / task069 Session 3 / task070 Sessions 2-3。
