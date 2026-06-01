# task245 Runbook Verification Report

<!-- METADATA:STATUS=BlockedForGate,ASSIGNEE=intern_nemotron_worker_5,SESSION=2 -->

## Summary

PR #317 persists the artifact/runbook verification requested by task245. This
is verification documentation only: no training, live eval, endpoint serving,
30B/8-GPU scale, shared-file deletion, merge, or `main` push was performed.

Current gate verdict: **BLOCKED for first Qwen3-4B AIME go/no-go readiness**.
Resolved since the prior report: task241 PR #320 is open/CLEAN at `5753713`
with V10 data-prep code/report present, and task243 PR #319 is open/CLEAN at
`61a12dd` with the Qwen3-4B AIME gate configured to the verified cephfs base
path. The gate remains blocked only on the current blockers listed below:
task242 has no published PR, the corrected AIME input/cache is missing, no
reachable Qwen3-4B endpoint exists, no base score artifacts exist, no candidate
FT checkpoint/export/eval exists, and 30B scale has no permission.

## Inputs Inspected

| Input | Status |
| --- | --- |
| PR #317 `intern_nemotron_worker_5/task245_qwen_aime_v10_artifact_runbook_verify_s1` | Open/CLEAN; this refresh is based on pre-edit head `ba3c2a1` |
| task241 PR #320 @ `5753713` | Open/CLEAN; V10 data-prep code/report present, including `hard_math_runlength_dp_v10`, `prepare_m1_agentic_sft.py`, and `v10_sidecar_data_report.md`; no training or live eval run |
| task242 branch `origin/intern_nemotron_worker_2/task242_qwen_aime_v10_planner_smoke_s1` @ `b2d16a7` | Remote branch contains task/status docs only; no PR found |
| task242 local worker_2 workspace | Uncommitted V10 planner diff previously observed; used only for non-launch planner-shape probes |
| task243 PR #319 @ `61a12dd` | Open/CLEAN; gate module/config/report present and Qwen3-4B base path now matches the verified cephfs path |
| task244 PR #318 @ `e5f4677` | Open/CLEAN; independent review exists but may predate the #319/#320 state refresh |
| `origin/main` | `f5a844765c5ac1a756b7f7e94d27ee466fe25a9b` |

## Verified Paths

| Artifact | Path | Verification |
| --- | --- | --- |
| Qwen3-4B base model, approved for the 4B pilot | `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507` | Exists, `du -sh` reported `7.6G`; top-level model/tokenizer files present |
| Qwen3-30B-A3B model, scale held | `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507` | Exists, `du -sh` reported `57G`; not used or launched |
| task243 Qwen3-4B AIME gate base path | `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507` | PR #319 head `61a12dd` config points here; matches the verified accessible base path |
| task241 V10 data-prep code | `origin/pr/320:src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py` | Present in PR #320 with `hard_math_runlength_dp_v10` |
| task241 V10 data-prep report | `origin/pr/320:workspace/tasks/task241_qwen_aime_v10_sidecar_data_s1/v10_sidecar_data_report.md` | Present in PR #320 |
| task243 corrected AIME runner | `workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/run_corrected_math_full_eval.py` | Exists in worker_5 and worker_3 worktrees |
| task243 cited AIME score cache | `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/aime_score_cache.db` | Missing in this workspace |
| Shared no-delete root | `/mnt/cephfs/data/processing/lei.song` | Exists and was only listed; current listing was empty |

## Expected Artifact Paths

These are the paths task245 expects before the first measurable go/no-go can be
declared. Task241 data-prep code/report are now published in PR #320. Paths
under task242 are still derived from the observed local planner shape and remain
conditional until worker_2 publishes and review-gates the planner PR.

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
| Local CPU prep | Run from local CPU first; include V10 strategy, Qwen3-4B model/tokenizer, held-out decontamination corpus, Qwen chat template kwargs `enable_thinking=false`, `truncate_history_thinking=false` | PARTIAL: task241 PR #320 publishes V10 data-prep code/report; BLOCKED until task242 publishes planner scripts/manifest and the corrected AIME input/cache is available |
| Decontamination | V10 must fail closed without `--decontaminate-math-against-corpus`; AIME25/HMMT/MATH prompts are held-out only | REVIEWED: PR #320 implements the V10 decontamination contract; release evidence still requires the exact corrected AIME input/cache and review-gated task242 repro artifacts |
| 30B hold | V10 30B planning must be held until the Qwen3-4B same-harness AIME gate passes and lead grants scale permission | HELD: no 30B/8-GPU launch was run and no 30B scale permission exists |
| Sync to NemTron | Sync code and bundle to `/root/...` on NemTron; any cleanup must be restricted to the task-owned `/root/task242_qwen_aime_v10_planner_smoke_s1` tree | CONDITIONAL: task242 has no published PR; previously observed local planner shape restricted cleanup to task-owned `/root` paths and never to shared `/mnt/cephfs/data/processing/lei.song` |
| Remote train | Qwen3-4B pilot only; no 30B/8-GPU scale; expected `CUDA_VISIBLE_DEVICES=0,1`, `nproc_per_node=2` in the local planner probe | NOT RUN by task boundary |
| Endpoint serving | Serve base and FT through `/v1/chat/completions` with identical route/settings | BLOCKED: no endpoint command or live endpoint artifact supplied; curls to `127.0.0.1:13000` and `127.0.0.1:30001` failed with connection refused |
| Corrected AIME pilot smoke | 30 AIME 2025 problems x 1 repeat, max tokens `8192`, temperature `0.0`, top_p `1e-5`, exact-normalized scoring over all request rows | Defined by task243 PR #319; corrected AIME input/cache and live base score artifacts are still missing |
| Full AIME protocol | 30 AIME 2025 problems x 10 repeats, same parser/scorer/settings as pilot except repeat count | Defined by task243 PR #319; not required before first pilot go/no-go |
| Result collection | Persist numerator, denominator, exact-normalized accuracy, parsed count/rate, finish reasons, per-problem rows, status counts, command, endpoint model manifest | BLOCKED: no base or FT output artifacts exist |

## Task243 Base-Score Verification Before FT Judgment

Before any FT result is judged, worker_5 should verify the base artifacts from
task243 or a lead-approved successor as follows:

1. Confirm task243 gate config/report uses an accessible base model path. PR
   #319 head `61a12dd` uses
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`, which exists
   in this workspace and matches the approved Qwen3-4B pilot path.
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

Session 1 task243 unit check run:

```bash
PYTHONPATH=src pytest -q tests/recipes/super3/test_qwen_aime2025_base_vs_ft_gate.py
```

Observed result: `7 passed in 0.09s`.

## Current Blockers

1. **task242 has no published PR**: the remote branch currently contains
   task/status docs only. The V10 pilot planner scripts, manifest, sync/runbook,
   and cleanup contract are not reviewable PR artifacts yet.
2. **Corrected AIME input/cache is missing**: the cited score-cache path
   `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/aime_score_cache.db`
   is not visible in this workspace.
3. **No reachable Qwen3-4B endpoint**: `curl` probes to `127.0.0.1:13000/v1/models` and
   `127.0.0.1:30001/v1/models` returned connection refused.
4. **No 4B base-score artifacts**: without task243 base `summary.json`,
   `results.jsonl`, `command.txt`, and endpoint manifest, FT judgment must be
   blocked.
5. **No candidate FT checkpoint/export/eval**: expected checkpoint, HF export,
   eval output, and train/eval logs are not present, so same-harness
   base-vs-FT AIME25 cannot be reproduced yet.
6. **No 30B scale permission**: 30B/8-GPU planning and launch remain held until
   the Qwen3-4B same-harness AIME gate is independently satisfied and lead
   grants explicit scale permission.

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
gh pr view 317 --json number,state,headRefName,headRefOid,mergeStateStatus,url
gh pr view 319 --json number,state,headRefName,headRefOid,mergeStateStatus,url
gh pr view 320 --json number,state,headRefName,headRefOid,mergeStateStatus,url
gh pr view 318 --json number,state,headRefName,headRefOid,mergeStateStatus,url
git fetch origin pull/319/head:refs/remotes/origin/pr/319 pull/320/head:refs/remotes/origin/pr/320
git show origin/pr/319:src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_aime2025_base_vs_ft_gate.yaml | sed -n '1,40p'
git ls-tree -r --name-only origin/pr/320
git show origin/pr/320:workspace/tasks/task241_qwen_aime_v10_sidecar_data_s1/v10_sidecar_data_report.md | sed -n '1,120p'
git show origin/pr/320:src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py | rg -n "hard_math_runlength_dp_v10|decontaminate-math-against-corpus|AIME-25|HMMT"
test -d /mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507
du -sh /mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507
test -d /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507
du -sh /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507
test -f /work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/aime_score_cache.db
curl -sS --connect-timeout 2 --max-time 4 http://127.0.0.1:13000/v1/models
curl -sS --connect-timeout 2 --max-time 4 http://127.0.0.1:30001/v1/models
```

Session 1 local worker_2 planner-shape probes were also run without launching
training:

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
decontamination corpus, candidate FT checkpoint path, and 30B hold rule. It is
not accepted as release evidence because task242 still has no published PR.

## Go/No-Go Readiness

Current status: **NO-GO** for judging the first Qwen3-4B V10 FT checkpoint and
**NO-GO** for any 30B/8-GPU scale proposal.

The first measurable gate becomes ready only when all of the following are
present and independently verified:

1. task241 PR #320 remains reviewable for V10 data-prep code/report evidence,
   including decontamination scanned/dropped counts, sidecar row counts, and
   no AIME25/HMMT/MATH leakage evidence.
2. task242 publishes the Qwen3-4B V10 pilot manifest/scripts and the scripts
   fail closed on missing decontamination corpus while restricting cleanup to
   task-owned `/root` paths.
3. task243 produces same-harness base AIME25 pilot artifacts from the verified
   cephfs Qwen3-4B base path before any FT judgment.
4. A candidate FT checkpoint/export is produced under the documented task-owned
   path and served through the same route/protocol as the base.
5. task243 comparison artifacts show
   `ft_exact_normalized_accuracy >= base_exact_normalized_accuracy` with
   parsed/finish/per-problem diagnostics included.
6. Lead grants explicit permission before any 30B/8-GPU scale action.
