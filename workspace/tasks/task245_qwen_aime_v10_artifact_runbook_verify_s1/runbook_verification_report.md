# task245 Runbook Verification Report

<!-- METADATA:STATUS=BlockedForGate,ASSIGNEE=intern_nemotron_worker_5,SESSION=1 -->

## Summary

PR #317 now persists the artifact/runbook verification requested by task245.
This is verification documentation only: no training, live eval, endpoint
serving, 30B/8-GPU scale, shared-file deletion, merge, or `main` push was
performed.

Current gate verdict: **BLOCKED for first Qwen3-4B AIME go/no-go readiness**.
The base Qwen3-4B model path is verified, and task243 PR #319 defines a
same-harness AIME25 base-vs-FT gate whose unit tests pass. However, the V10
data/planner artifacts are not yet published as reviewable PR artifacts, the
task243 base config still names a missing `/mnt/3fs` path, no corrected base
score artifacts exist in this workspace, no Qwen endpoint is listening, and no
candidate FT checkpoint/export/eval output exists.

## Inputs Inspected

| Input | Status |
| --- | --- |
| PR #317 `intern_nemotron_worker_5/task245_qwen_aime_v10_artifact_runbook_verify_s1` | Open; this report added after head `aa071c4` |
| task241 branch `origin/intern_nemotron_worker_1/task241_qwen_aime_v10_sidecar_data_s1` @ `233a0e0` | Remote branch contains task/status docs only; no PR found |
| task241 local worker_1 workspace | Uncommitted V10 data-prep diff observed; not accepted as PR evidence |
| task242 branch `origin/intern_nemotron_worker_2/task242_qwen_aime_v10_planner_smoke_s1` @ `b2d16a7` | Remote branch contains task/status docs only; no PR found |
| task242 local worker_2 workspace | Uncommitted V10 planner diff observed; used only for non-launch planner-shape probes |
| task243 PR #319 @ `bfb49a8` | Open; gate module/config/report present; tests pass locally |
| task244 PR #318 @ `069424b` | Open; independent review blocks #317 until this report exists |
| `origin/main` | `f5a844765c5ac1a756b7f7e94d27ee466fe25a9b` |

## Verified Paths

| Artifact | Path | Verification |
| --- | --- | --- |
| Qwen3-4B base model, approved for the 4B pilot | `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507` | Exists, `du -sh` reported `7.6G`; top-level model/tokenizer files present |
| Qwen3-30B-A3B model, scale held | `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507` | Exists, `du -sh` reported `57G`; not used or launched |
| task243 configured Qwen3-4B base path | `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507` | Missing in this workspace; path mismatch must be fixed or explicitly mapped before base scoring |
| task243 corrected AIME runner | `workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/run_corrected_math_full_eval.py` | Exists in worker_5 and worker_3 worktrees |
| task243 cited AIME score cache | `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/aime_score_cache.db` | Missing in this workspace |
| Shared no-delete root | `/mnt/cephfs/data/processing/lei.song` | Exists and was only listed; current listing was empty |

## Expected Artifact Paths

These are the paths task245 expects before the first measurable go/no-go can be
declared. Paths under task242 are derived from the observed local planner shape;
they remain conditional until worker_2 publishes and review-gates the planner
PR.

| Stage | Expected path | Current status |
| --- | --- | --- |
| Local pilot bundle root | `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot` | Not present as a published artifact |
| Local M0 prep | `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/m0_agentic` | Missing |
| Local M1 V10 data | `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/m1_agentic_sft` | Missing |
| Local packed shards | `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/packed_qwen/splits` | Missing |
| Local planner manifest | `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/scaleup_manifest.json` | Missing |
| Local generated scripts | `run_local_data_prep.sh`, `sync_to_nemtron.sh`, `run_nemtron_train.sh`, `run_eval_basket_dry_run.sh` under the pilot bundle root | Missing as published artifacts |
| NemTron sync root | `/root/task242_qwen_aime_v10_planner_smoke_s1` | Expected task-owned remote root |
| NemTron synced repo | `/root/task242_qwen_aime_v10_planner_smoke_s1/Nemotron` | Not verified on NemTron in this task |
| NemTron run root | `/root/task242_qwen_aime_v10_planner_smoke_s1/task242_qwen_aime_v10_4b_pilot` | Expected from default output-dir basename |
| NemTron packed shards | `/root/task242_qwen_aime_v10_planner_smoke_s1/task242_qwen_aime_v10_4b_pilot/packed_qwen/splits` | Missing until local prep/sync runs |
| NemTron train manifest | `/root/task242_qwen_aime_v10_planner_smoke_s1/task242_qwen_aime_v10_4b_pilot/training_plan/qwen_m1_agentic_sft_scaleup/training_manifest.json` | Missing |
| Candidate FT checkpoint | `/root/task242_qwen_aime_v10_planner_smoke_s1/task242_qwen_aime_v10_4b_pilot/checkpoints` | Missing |
| Candidate FT HF export | Not encoded in the currently observed planner output | BLOCKER: exact export path must be supplied before endpoint serving/eval |
| NemTron train log | `/root/task242_qwen_aime_v10_planner_smoke_s1/task242_qwen_aime_v10_4b_pilot/logs/train.log` | Missing |
| Base AIME output dir | A lead/PM-approved task243 output directory containing `summary.json`, `results.jsonl`, `command.txt`, `endpoint_model_manifest.json` | Missing |
| FT AIME output dir | Matching FT output directory containing the same four files | Missing |
| Comparison output | `base_vs_ft_gate_decision.json` and `base_vs_ft_gate_report.md` | Missing |

## Command And Protocol Checklist

| Step | Required command/protocol condition | Verification result |
| --- | --- | --- |
| Local CPU prep | Run from local CPU first; include V10 strategy, Qwen3-4B model/tokenizer, held-out decontamination corpus, Qwen chat template kwargs `enable_thinking=false`, `truncate_history_thinking=false` | BLOCKED: no published task241/task242 artifact; local worker_2 planner probe emitted the expected flags but is uncommitted evidence |
| Decontamination | V10 must fail closed without `--decontaminate-math-against-corpus`; AIME25/HMMT/MATH prompts are held-out only | PASS for local worker_2 planner probe: missing corpus returned rc=1 with explicit error; no train files were produced |
| 30B hold | V10 30B planning must be held until the Qwen3-4B same-harness AIME gate passes | PASS for local worker_2 planner probe: 30B V10 planning returned rc=1 without `--allow-v10-30b-scale`; no 30B launch |
| Sync to NemTron | Sync code and bundle to `/root/...` on NemTron; any cleanup must be restricted to the task-owned `/root/task242_qwen_aime_v10_planner_smoke_s1` tree | CONDITIONAL PASS: local planner probe generated `rm -rf /root/task242_qwen_aime_v10_planner_smoke_s1/Nemotron /root/task242_qwen_aime_v10_planner_smoke_s1/<run>` only; no shared `/mnt/cephfs/data/processing/lei.song` deletion |
| Remote train | Qwen3-4B pilot only; no 30B/8-GPU scale; expected `CUDA_VISIBLE_DEVICES=0,1`, `nproc_per_node=2` in the local planner probe | NOT RUN by task boundary |
| Endpoint serving | Serve base and FT through `/v1/chat/completions` with identical route/settings | BLOCKED: no endpoint command or live endpoint artifact supplied; curls to `127.0.0.1:13000` and `127.0.0.1:30001` failed with connection refused |
| Corrected AIME pilot smoke | 30 AIME 2025 problems x 1 repeat, max tokens `8192`, temperature `0.0`, top_p `1e-5`, exact-normalized scoring over all request rows | Defined by task243 PR #319; no live base score produced |
| Full AIME protocol | 30 AIME 2025 problems x 10 repeats, same parser/scorer/settings as pilot except repeat count | Defined by task243 PR #319; not required before first pilot go/no-go |
| Result collection | Persist numerator, denominator, exact-normalized accuracy, parsed count/rate, finish reasons, per-problem rows, status counts, command, endpoint model manifest | BLOCKED: no base or FT output artifacts exist |

## Task243 Base-Score Verification Before FT Judgment

Before any FT result is judged, worker_5 should verify the base artifacts from
task243 or a lead-approved successor as follows:

1. Confirm task243 gate config/report uses an accessible base model path. The
   current PR #319 config uses `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`,
   which is missing here; the verified accessible path is
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
2. Confirm the base output directory contains exactly these minimum artifacts:
   `summary.json`, `results.jsonl`, `command.txt`, and
   `endpoint_model_manifest.json`.
3. Check `command.txt` or equivalent metadata records `/v1/chat/completions`,
   AIME25 original corrected prompt set, `8192` max tokens,
   `temperature=0.0`, `top_p=1e-5`, one repeat per problem for the pilot,
   and the exact-normalized scorer.
4. Check `endpoint_model_manifest.json` identifies the served base model as
   Qwen3-4B and points to the approved base checkpoint/tokenizer path.
5. Check `summary.json` records all required diagnostics: numerator,
   denominator, exact-normalized accuracy, parsed count/rate, finish reason
   counts, status counts, and per-problem rows.
6. Refuse FT judgment if the FT command/protocol differs from the base in model
   family, route, prompt set, repeats, max tokens, parser, sampling policy, or
   scorer normalization.
7. Run or inspect task243 gate comparison output and require status
   `pass_ft_at_least_base`; status `blocked_missing_base`,
   `blocked_missing_ft`, or `fail_ft_below_base` keeps 30B/8-GPU scale held.

Task243 PR #319 unit check run:

```bash
PYTHONPATH=src pytest -q tests/recipes/super3/test_qwen_aime2025_base_vs_ft_gate.py
```

Observed result: `7 passed in 0.09s`.

## Current Blockers

1. **No published V10 data implementation/artifacts**: task241 remote branch
   currently contains task/status docs only. Local worker_1 uncommitted diff
   shows a V10 strategy name and filters, but there is no PR, data report,
   decontamination report, train JSONL, sidecar row count, packed shard, or
   no-leakage test artifact to verify.
2. **No published V10 planner artifacts**: task242 remote branch currently
   contains task/status docs only. Local worker_2 uncommitted planner probe
   generated a plausible Qwen3-4B V10 bundle shape and fail-closed checks, but
   the scripts/manifest are not reviewable PR artifacts.
3. **Base path mismatch in task243**: PR #319 pins
   `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`, which is
   missing here. The accessible base model is
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
4. **Corrected AIME input artifact missing**: the cited score-cache path
   `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/aime_score_cache.db`
   is not visible in this workspace.
5. **No live endpoint**: `curl` probes to `127.0.0.1:13000/v1/models` and
   `127.0.0.1:30001/v1/models` returned connection refused.
6. **No candidate FT checkpoint/export**: expected checkpoint/export/eval/log
   paths are not present, so same-harness base-vs-FT AIME25 cannot be
   reproduced yet.
7. **No 4B base-score artifacts**: without task243 base `summary.json`,
   `results.jsonl`, `command.txt`, and endpoint manifest, FT judgment must be
   blocked.

## No-Delete Shared Storage Guarantee

- This task performed read-only filesystem probes and repository inspection
  only. It did not delete files.
- `/mnt/cephfs/data/processing/lei.song` was listed and found present; no
  commands wrote to or removed from it.
- Any future sync/cleanup step must be restricted to task-owned local output
  directories or `/root/task242_qwen_aime_v10_planner_smoke_s1` on NemTron.
- No runbook step may use `rm`, `rm -rf`, `find -delete`, overwrite cleanup, or
  model/export cleanup under `/mnt/cephfs/data/processing/lei.song`.
- CPU-local downloads must happen outside the shared `lei.song` processing
  tree first, then be copied to NemTron only when needed.

## Verification Commands Run

```bash
test -d /mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507
du -sh /mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507
test -d /mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507
test -f /work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/aime_score_cache.db
curl -sS --connect-timeout 2 --max-time 4 http://127.0.0.1:13000/v1/models
curl -sS --connect-timeout 2 --max-time 4 http://127.0.0.1:30001/v1/models
PYTHONPATH=src pytest -q tests/recipes/super3/test_qwen_aime2025_base_vs_ft_gate.py
```

Local worker_2 planner-shape probes were also run without launching training:

```bash
PYTHONPATH=src python src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_qwen_scaleup_run.py \
  --qwen4b-v10-pilot \
  --output-dir /tmp/task245_worker2_plan_verify.<tmp>/out \
  --remote-root /root/task242_qwen_aime_v10_planner_smoke_s1 \
  --math-decontaminate-against-corpus /tmp/task245_worker2_plan_verify.<tmp>/heldout.jsonl \
  --allow-missing-checkpoint \
  --overwrite
```

The probe emitted the expected Qwen3-4B base path, V10 strategy,
decontamination corpus, candidate FT checkpoint path, and 30B hold rule, but
it is not accepted as release evidence because it was generated from
uncommitted local worker_2 changes.

## Go/No-Go Readiness

Current status: **NO-GO** for judging the first Qwen3-4B V10 FT checkpoint and
**NO-GO** for any 30B/8-GPU scale proposal.

The first measurable gate becomes ready only when all of the following are
present and independently verified:

1. task241 publishes V10 data-prep code/report with decontamination scanned and
   dropped counts, sidecar row counts, no AIME25/HMMT/MATH leakage evidence,
   and packed shard paths.
2. task242 publishes the Qwen3-4B V10 pilot manifest/scripts and the scripts
   fail closed on missing decontamination corpus while restricting cleanup to
   task-owned `/root` paths.
3. task243 aligns the base checkpoint path to an accessible path or documents a
   lead-approved mapping, then produces same-harness base AIME25 pilot
   artifacts.
4. A candidate FT checkpoint/export is produced under the documented task-owned
   path and served through the same route/protocol as the base.
5. task243 comparison artifacts show
   `ft_exact_normalized_accuracy >= base_exact_normalized_accuracy` with
   parsed/finish/per-problem diagnostics included.
