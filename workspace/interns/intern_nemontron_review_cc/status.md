# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=roadmap_refresh_and_gap_tasks -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | (cross-cutting) roadmap refresh + gap-task scaffolding |
| PR | pending push |
| Session | 71 |

正在做：roadmap refinement pass + new task scaffolds。User asked for a
top-level review of codebase + plan + roadmap, with refined task
statuses AND new tasks where gaps exist.

**Synthesis source**: Explore agent inventoried workspace tasks +
pipeline modules + plan-vs-repo coverage gap; identified 4 untracked
gaps and 3 task READMEs that needed Session 2 split refinement.

## Changes in this PR

### Roadmap refresh (`docs/implementation-roadmap.md`)

- Last-updated bumped to 2026-05-19 with summary of changes
- New "Current state snapshot (2026-05-19)" section at top:
  - Sandbox-runnable M1 layer complete; baseline 502 passed
  - Cluster-bound queue called out
  - **Recent learnings** subsection capturing task065 lessons
    (TBD revision, SWE-Gym real shape, HelpSteer-2 scalar rows)
- New §5b "Cluster vs sandbox work queue" section: explicit table of
  what's sandbox-pickable next vs what's cluster-blocked, with M2/M3
  task scaffolds explicitly deferred
- §4 cross-cutting task040 flipped from "cited not scaffolded" to
  "Session 0 ✓ scaffolded"

### 4 new task scaffolds (workspace/tasks/)

- **task040_w1_curriculum_sampler** — W1 difficulty curriculum sampler
  (was cited in roadmap §4 but never had a workspace dir; 4 sessions
  declared, Session 1 sandbox-runnable)
- **task070_openhands_loop_wrapper** — lifted from task017 Session 2
  OpenHands wrapper deferral (3 sessions, Session 1 sandbox-runnable
  with Protocol + FakeOpenHandsLoop stub)
- **task068_rlhf_toolcall_pairing_harness** — lifted from task018
  Session 2 tool-call pairing deferral (4 sessions, Session 1
  design-first; addresses naïve cross-product 200M-pair blow-up)
- **task069_wandb_artifact_lineage_publish** — lifted from task021
  Session 2 W&B publish deferral (3 sessions, Session 1 sandbox-
  runnable with injectable W&B run + FakeWandbRun double)

### Existing task README refinements

- **task013** README: Session 2 split into 2a (sandbox driver + YAML
  chain) + 2b (cluster verify) so the sandbox-runnable part has a
  visible pick-point
- **task017** README: OpenHands wrapper deferral now explicitly points
  at task070 as the formal owner (renamed from task067 after collision
  with `task067_m1_agentic_qwen_scaleup` from intern_nemontron_code_reading)
- **task018** README: tool-call pairing harness deferral now explicitly
  points at task068 as the formal owner
- **task021** README: Session 7 W&B publish row added pointing at
  task069

## 不动

- M2/M3 task scaffolds deliberately NOT created — earlier scaffolding
  without execution context risks scope drift; create when M1 freezes
- Code changes (no new modules); this is a planning-only refresh
- Cluster-side documentation; updates only reflect what landed
  pre-2026-05-19

Sandbox 测试基线 502 passed + 7 skipped (no change — no code edits)。
三个 data-registry audit 全 clean。
