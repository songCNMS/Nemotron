# task245 Runbook Verification Report

<!-- METADATA:STATUS=BlockedForGate,ASSIGNEE=intern_nemotron_worker_5,SESSION=3 -->

## Summary

PR #317 persists the artifact/runbook verification requested by task245. This
is verification documentation only: no training, live eval, endpoint serving,
30B/8-GPU scale, shared-file deletion, merge, or `main` push was performed.

Current gate verdict: **BLOCKED for first Qwen3-4B AIME go/no-go readiness**.
Resolved since the prior report:

- task241 PR #320 is open/CLEAN at `5753713` with V10 data-prep code/report.
- task242 PR #321 is open/CLEAN at `12ee98c` with the Qwen3-4B V10
  planner/smoke report and task-owned bundle paths.
- task243 PR #319 is open/CLEAN at `61a12dd` with the Qwen3-4B AIME gate
  configured to the verified cephfs base path.

The gate remains blocked on real evidence inputs and runtime artifacts: real
heldout decontamination corpus/input, corrected AIME input/cache, reachable
Qwen3-4B endpoint, base score artifacts, candidate FT checkpoint/export/eval,
and explicit 30B/8-GPU permission.

## Inputs Inspected

| Input | Status |
| --- | --- |
| PR #317 `intern_nemotron_worker_5/task245_qwen_aime_v10_artifact_runbook_verify_s1` | Open; this refresh is based on pre-edit head `b8d3c98` |
| task241 PR #320 @ `5753713` | Open/CLEAN; V10 data-prep code/report present, including `hard_math_runlength_dp_v10`, `prepare_m1_agentic_sft.py`, and `v10_sidecar_data_report.md`; no training or live eval run |
| task242 PR #321 @ `12ee98c` | Open/CLEAN; planner support and smoke report present, including `plan_qwen_scaleup_run.py`, `test_m1_agentic_qwen_scaleup_plan.py`, and `planner_report.md`; no training or live eval run |
| task243 PR #319 @ `61a12dd` | Open/CLEAN; gate module/config/report present and Qwen3-4B base path matches the verified cephfs path |
| task244 PR #318 @ `e5f4677` | Open/CLEAN; independent review exists but may predate the #321 state refresh |
| `origin/main` | `f5a844765c5ac1a756b7f7e94d27ee466fe25a9b` |

## Verified Paths

| Artifact | Path | Verification |
| --- | --- | --- |
| Qwen3-4B base model, approved for the 4B pilot | `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507` | Exists, `du -sh` reported `7.6G`; top-level model/tokenizer files present |
| Qwen3-30B-A3B model, scale held | `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507` | Exists, `du -sh` reported `57G`; not used or launched |
| task243 Qwen3-4B AIME gate base path | `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507` | PR #319 head `61a12dd` config points here; matches the verified accessible base path |
| task241 V10 data-prep code | `origin/pr/320:src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py` | Present in PR #320 with `hard_math_runlength_dp_v10` |
| task241 V10 data-prep report | `origin/pr/320:workspace/tasks/task241_qwen_aime_v10_sidecar_data_s1/v10_sidecar_data_report.md` | Present in PR #320 |
| task242 Qwen3-4B V10 planner code | `origin/pr/321:src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_qwen_scaleup_run.py` | Present in PR #321; publishes Qwen3-4B V10 profile, decontamination fail-closed checks, and 30B hold |
| task242 planner/smoke report | `origin/pr/321:workspace/tasks/task242_qwen_aime_v10_planner_smoke_s1/planner_report.md` | Present in PR #321 |
| task242 local smoke bundle files | `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot` | Files present: `scaleup_manifest.json`, `report.md`, `run_local_data_prep.sh`, `sync_to_nemtron.sh`, `run_nemtron_train.sh`, `run_eval_basket_dry_run.sh`, and placeholder decontam corpus |
| task242 placeholder decontam corpus | `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/aime25_hmmt_math_heldout_decontam_corpus.PLACEHOLDER.jsonl` | Present with one placeholder row; not accepted as real heldout corpus evidence |
| task243 corrected AIME runner | `workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/run_corrected_math_full_eval.py` | Exists in worker_5 and worker_3 worktrees |
| task243 cited AIME score cache | `/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/aime_score_cache.db` | Missing in this workspace |
| Shared no-delete root | `/mnt/cephfs/data/processing/lei.song` | Exists and was only listed; current listing was empty |

## Expected Artifact Paths

These are the paths task245 expects before the first measurable go/no-go can be
declared. Task241 data-prep code/report are published in PR #320, and task242
planner/smoke paths are published in PR #321. The actual run evidence is still
blocked until real heldout decontamination input replaces the placeholder and
the Qwen3-4B base/FT AIME artifacts are produced.

| Stage | Expected path | Current status |
| --- | --- | --- |
| Local pilot bundle root | `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot` | Present in worker_2 output and documented by #321 |
| Local M0 prep input | `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/task241_v10_math_sidecar_m0_PENDING` | Placeholder path only; real task241-derived input still required before prep |
| Real heldout decontam corpus | A lead/PM-approved AIME25/HMMT/MATH heldout prompt corpus path | Missing; #321 placeholder intentionally fails closed |
| Local M1 V10 data | `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/m1_agentic_sft` | Missing until real data prep runs |
| Local packed shards | `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/packed_qwen/splits` | Missing until packing runs |
| Local planner manifest | `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/scaleup_manifest.json` | Present in worker_2 output and documented by #321 |
| Local generated scripts | `run_local_data_prep.sh`, `sync_to_nemtron.sh`, `run_nemtron_train.sh`, `run_eval_basket_dry_run.sh` under the pilot bundle root | Present in worker_2 output and documented by #321; not executed here |
| NemTron sync root | `/root/task242_qwen_aime_v10_planner_smoke_s1` | Expected task-owned remote root from #321 |
| NemTron synced repo | `/root/task242_qwen_aime_v10_planner_smoke_s1/Nemotron` | Not verified on NemTron in this task |
| NemTron run root | `/root/task242_qwen_aime_v10_planner_smoke_s1/task242_qwen_aime_v10_4b_pilot` | Expected from #321 |
| NemTron packed shards | `/root/task242_qwen_aime_v10_planner_smoke_s1/task242_qwen_aime_v10_4b_pilot/packed_qwen/splits` | Missing until local prep/sync runs |
| NemTron train manifest | `/root/task242_qwen_aime_v10_planner_smoke_s1/task242_qwen_aime_v10_4b_pilot/training_plan/qwen_m1_agentic_sft_scaleup/training_manifest.json` | Missing |
| Candidate FT checkpoint | `/root/task242_qwen_aime_v10_planner_smoke_s1/task242_qwen_aime_v10_4b_pilot/checkpoints` | Expected by #321; missing because training was not run |
| Candidate FT HF export | A documented task-owned export path for the candidate FT checkpoint | Missing; must be supplied before endpoint serving/eval |
| NemTron train log | `/root/task242_qwen_aime_v10_planner_smoke_s1/task242_qwen_aime_v10_4b_pilot/logs/train.log` | Missing |
| Base AIME output dir | A lead/PM-approved task243 output directory containing `summary.json`, `results.jsonl`, `command.txt`, `endpoint_model_manifest.json` | Missing |
| FT AIME output dir | Matching FT output directory containing the same four files | Missing |
| Comparison output | `base_vs_ft_gate_decision.json` and `base_vs_ft_gate_report.md` | Missing |

## Command And Protocol Checklist

| Step | Required command/protocol condition | Verification result |
| --- | --- | --- |
| Local CPU prep | Run from local CPU first; include V10 strategy, Qwen3-4B model/tokenizer, real heldout decontamination corpus, Qwen chat template kwargs `enable_thinking=false`, `truncate_history_thinking=false` | PARTIAL: task241 PR #320 and task242 PR #321 publish the code/report surface; BLOCKED until real heldout decontam corpus/input and corrected AIME input/cache are available |
| Decontamination | V10 must fail closed without `--decontaminate-math-against-corpus`; AIME25/HMMT/MATH prompts are held-out only | REVIEWED: PR #320 implements the V10 contract and PR #321 rejects missing/empty/placeholder corpora; release evidence still requires the real corpus/input |
| 30B hold | V10 30B planning must be held until the Qwen3-4B same-harness AIME gate passes and lead grants scale permission | HELD: #321 encodes the hold; no 30B/8-GPU launch was run and no 30B permission exists |
| Sync to NemTron | Sync code and bundle to `/root/...` on NemTron; cleanup must stay inside task-owned `/root/task242_qwen_aime_v10_planner_smoke_s1` paths | REVIEWED: #321 generated sync script refuses non-`/root/*` V10 remote roots and documents that it does not delete `/mnt/cephfs/data/processing/lei.song`; not executed here |
| Remote train | Qwen3-4B pilot only; no 30B/8-GPU scale; #321 report records the expected task-owned remote run root and candidate checkpoint path | NOT RUN by task boundary |
| Endpoint serving | Serve base and FT through `/v1/chat/completions` with identical route/settings | BLOCKED: no endpoint command or live endpoint artifact supplied; curls to `127.0.0.1:13000` and `127.0.0.1:30001` failed with connection refused |
| Corrected AIME pilot smoke | 30 AIME 2025 problems x 1 repeat, max tokens `8192`, temperature `0.0`, top_p `1e-5`, exact-normalized scoring over all request rows | Defined by task243 PR #319 and encoded by task242 PR #321; corrected AIME input/cache and live base score artifacts are still missing |
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

1. **Real heldout decontamination corpus/input is missing**: #321 publishes a
   placeholder corpus only to materialize paths and explicitly fail closed; the
   trusted AIME25/HMMT/MATH heldout corpus and real task241-derived local input
   must be supplied before data prep.
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
6. **No 30B/8-GPU permission**: 30B/8-GPU planning and launch remain held until
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
gh pr view 321 --json number,state,headRefName,headRefOid,mergeStateStatus,url
gh pr view 318 --json number,state,headRefName,headRefOid,mergeStateStatus,url
git fetch origin pull/321/head:refs/remotes/origin/pr/321 pull/319/head:refs/remotes/origin/pr/319 pull/320/head:refs/remotes/origin/pr/320
git show origin/pr/319:src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_aime2025_base_vs_ft_gate.yaml | sed -n '1,40p'
git show origin/pr/320:workspace/tasks/task241_qwen_aime_v10_sidecar_data_s1/v10_sidecar_data_report.md | sed -n '1,120p'
git show origin/pr/321:workspace/tasks/task242_qwen_aime_v10_planner_smoke_s1/planner_report.md | sed -n '1,180p'
git grep -n "qwen4b-v10-pilot|hard_math_runlength_dp_v10|decontaminate|/root/task242|30B|allow-v10-30b" origin/pr/321 -- src tests workspace/tasks/task242_qwen_aime_v10_planner_smoke_s1
find /work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot -maxdepth 1 -type f -printf '%f\n' | sort
sed -n '1,5p' /work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/aime25_hmmt_math_heldout_decontam_corpus.PLACEHOLDER.jsonl
test -d /mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507
du -sh /mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507
test -d /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507
du -sh /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507
test -f /work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/aime_score_cache.db
curl -sS --connect-timeout 2 --max-time 4 http://127.0.0.1:13000/v1/models
curl -sS --connect-timeout 2 --max-time 4 http://127.0.0.1:30001/v1/models
```

No training, live eval, endpoint serving, NemTron sync, shared-storage delete,
merge, or `main` push was run.

## Go/No-Go Readiness

Current status: **NO-GO** for judging the first Qwen3-4B V10 FT checkpoint and
**NO-GO** for any 30B/8-GPU scale proposal.

The first measurable gate becomes ready only when all of the following are
present and independently verified:

1. task241 PR #320 remains reviewable for V10 data-prep code/report evidence,
   including decontamination scanned/dropped counts, sidecar row counts, and
   no AIME25/HMMT/MATH leakage evidence.
2. task242 PR #321 remains reviewable for the Qwen3-4B V10 pilot
   manifest/scripts, fail-closed decontamination checks, task-owned `/root`
   cleanup limits, and 30B hold.
3. The placeholder decontamination corpus/input is replaced with trusted real
   heldout AIME25/HMMT/MATH corpus/input before any data prep.
4. task243 produces same-harness base AIME25 pilot artifacts from the verified
   cephfs Qwen3-4B base path before any FT judgment.
5. A candidate FT checkpoint/export is produced under the documented task-owned
   path and served through the same route/protocol as the base.
6. task243 comparison artifacts show
   `ft_exact_normalized_accuracy >= base_exact_normalized_accuracy` with
   parsed/finish/per-problem diagnostics included.
7. Lead grants explicit permission before any 30B/8-GPU scale action.
