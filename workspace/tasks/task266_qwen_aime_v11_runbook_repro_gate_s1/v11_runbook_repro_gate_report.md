# task266 V11 runbook/repro gate report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_5,SESSION=1 -->

## Summary

- Recommendation for task266: PASS as a static V11 runbook/repro gate.
- Recommendation for V11 execution: HOLD / NO-GO until task262-task265 publish
  the required exact artifacts, branch heads, reports, and review decisions.
- Branch:
  `intern_nemotron_worker_5/task266_qwen_aime_v11_runbook_repro_gate_s1`.
- Base: `origin/main` at `513fefa1f1ace94302b56413769c78fb7224624c`.
- Lead docs source:
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at
  `81253415dd3285ce0eb56e69733d210742edcb50`.
- Scope executed: read-only runbook and reproducibility gate across visible
  task262/task263/task264/task265 evidence, plus task260/task261 root-cause
  reports and task243/task247 same-harness base evidence.
- Boundary kept: no training, eval, export, endpoint launch, merge,
  promotion, 30B/8-GPU authorization, AIME2025 train-data use, shared deletion,
  or worker branch alteration.

The first measurable V11 go/no-go remains:

`new_qwen3_4b_ft_exact_normalized_accuracy >= 11/30`

under the same corrected AIME2025 30x1 harness, after base-load/import proof,
nonzero-LR training evidence, non-AIME canary pass, reviewer-readable artifacts,
and independent contamination/regression review exist.

## Evidence Inventory Checked

| Surface | Visible evidence | Current status |
|---|---|---|
| task262 data/packing repair | Lead assignment docs; remote branch `origin/intern_nemotron_worker_1/task262_qwen_aime_v11_data_split_sidecar_s1` at `e8c0df6f7c5885d5ace704e2f03b8ce77fc77bc3`; no PR; diff is status/task docs only | HOLD: no V11 data report, rebuilt artifacts, collision-free split proof, or sidecar checksum evidence yet |
| task263 base-load planner sanity | Lead assignment docs; worker_2 local task/status files exist, but no matching remote branch or PR was visible by `git ls-remote`/`gh pr list` | BLOCK for execution: no published base-load/import proof, no nonzero-LR schedule artifact, no NemTron smoke plan evidence |
| task264 canary/retention gate | Lead assignment docs; remote branch `origin/intern_nemotron_worker_3/task264_qwen_aime_v11_eval_gate_canary_retention_s1` at `b2a67412c412b7dd2f3f775f029049b49eef7a7b`; no PR; remote diff is status/task docs only | HOLD: canary prompt source, hashes, retention schema, and gate report are not published |
| task265 independent review | Lead assignment docs; remote branch points to `513fefa1f1ace94302b56413769c78fb7224624c` with no diff from main; no PR; worker_4 local task docs not visible | BLOCK for final clearance: independent contamination/regression matrix is not available |
| task260 failure forensics | Merged PR #332; report says task255 FT failure is generation degeneration/corruption, not evaluator-only parser failure | Used as V11 canary/retention requirement source |
| task261 root cause | Merged PR #333; report identifies likely missing Qwen base load, zero LR at only step, and split basename collisions | Used as V11 data/base-load/schedule gate source |
| task247 accepted base | Merged base artifact: Qwen3-4B exact-normalized AIME2025 `11/30 = 0.36666666666666664` | Fixed comparator for first V11 go/no-go |

## Required Paths

Stable Qwen3-4B base path:

`/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`

Verified in this review:

- `config.json`:
  `5beea1a4a34c62782bfb2f911c606741a3bab8f92d80a118fa053c28af12e8ba`
- `tokenizer_config.json`:
  `a62ff0a2472a0fa1b8eaabcb57c59b58afa42a22831dc141400b6e0cf2b65ce3`
- `tokenizer.json`:
  `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4`
- Config shape:
  `Qwen3ForCausalLM`, `model_type=qwen3`, 36 layers, hidden size 2560,
  32 attention heads, 8 KV heads, intermediate size 9728, vocab size 151936.

Corrected AIME2025 base input/cache from task247:

- Local cache:
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache/aime_score_cache.opencompass_a6ad95f.db`
- Remote runner cache:
  `/root/task247_qwen_aime2025_qwen4b_base_smoke_s1/input/aime_score_cache.opencompass_a6ad95f.db`
- Source dataset revision:
  `opencompass/AIME2025@a6ad95f611d72cf628a80b58bd0432ef6638f958`
- Cache sha256 from task247/task260:
  `c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74`

Shared storage boundary:

`/mnt/cephfs/data/processing/lei.song`

Verified in this review as `directory root:root 755`. Existing files under this
tree must not be deleted or overwritten.

Expected V11 task output roots:

- task262:
  `/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1/`
- task263:
  `/work-agents/intern_nemotron_worker_2/outputs/task263_qwen_aime_v11_base_load_planner_sanity_s1/`
- task264:
  `/work-agents/intern_nemotron_worker_3/outputs/task264_qwen_aime_v11_eval_gate_canary_retention_s1/`
- task265:
  `/work-agents/intern_nemotron_worker_4/outputs/task265_qwen_aime_v11_contam_regression_review_s1/`
- task266:
  `/work-agents/intern_nemotron_worker_5/outputs/task266_qwen_aime_v11_runbook_repro_gate_s1/`

## Stage Gate Matrix

| Stage | Required evidence | Current visible evidence | Gate |
|---|---|---|---|
| 1. V11 data/packing ready | task262 report with collision-free split materialization or fail-closed assertion; intended-vs-exposed rows/tokens/shards; hard-math/final-answer sidecar paths, counts, hashes; decontamination evidence; no AIME2025 train rows | task262 remote branch is acceptance/status docs only; no output root artifacts found | HOLD/BLOCK: no training may start |
| 2. Base-load/import proof ready | task263 report proving Qwen3-4B base weight load or Bridge-approved HF import; positive load line or import manifest; base hashes; abort checks for random-init loss, NaN/Inf, zero LR; nonzero first-step LR schedule; NemTron sync path | no published task263 branch/PR; worker_2 local status says accepted only | HOLD/BLOCK: no checkpoint/export may be accepted |
| 3. Non-AIME canary ready | task264 canary prompt set with source/hashes; proof prompts are not AIME2025 and not train rows; config/tokenizer parity checks; retention schema for full completions/debug transcript | task264 remote branch is acceptance/status docs only; local dirty changes are not reviewed as published evidence | HOLD: no AIME eval may be requested |
| 4. Bounded Qwen3-4B pilot allowed | Stages 1-3 PASS, lead clearance, Qwen3-4B only, code synced to task-owned `/root` run dir on NemTron, no AIME2025 train data, no task255 reuse | missing stages 1-3 | NO-GO |
| 5. Same-harness AIME comparison allowed | New V11 FT artifact is reviewer-readable with manifest/hash checks, canary pass, base protocol parity, task265 review not blocking; use accepted task247 cache/protocol | no V11 FT candidate exists | NO-GO |
| 6. Promotion/non-regression decision | FT exact-normalized AIME25 score `>= 11/30` under same 30x1 pilot protocol, and full promotion only after lead-defined full protocol; no 30B/8-GPU without explicit permission | no V11 same-harness result exists | NO-GO/HOLD |

## Command Templates

These commands are templates or read-only verification commands. They are not
authorization to train, eval, export, launch endpoints, merge, promote, or use
30B/8-GPU.

### Source And Branch Visibility

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git rev-parse origin/main origin/intern_nemotron_lead/session1-recovery-task-docs
git ls-remote --heads origin 'intern_nemotron_worker_*/task26*_qwen_aime_v11*'
gh pr list --state all --head <branch> --json number,title,state,headRefOid,baseRefName,mergeStateStatus,mergedAt,url
```

### Qwen3-4B Base Path Check

```bash
BASE=/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507
test -d "$BASE"
sha256sum "$BASE/config.json" "$BASE/tokenizer_config.json" "$BASE/tokenizer.json"
jq '{architectures, model_type, num_hidden_layers, hidden_size, num_attention_heads, num_key_value_heads, intermediate_size, vocab_size}' "$BASE/config.json"
```

### Shared Storage No-Delete Check

```bash
stat -c '%F %U:%G %a %n' /mnt/cephfs/data/processing/lei.song
```

Reviewers must reject any plan that uses destructive commands under
`/mnt/cephfs/data/processing/lei.song`. Task-owned new subdirectories may be
created only when the task requires it and must not overwrite existing shared
files.

### NemTron Sync Template

Before any debug run on `NemTron`, code must be synced to a task-owned `/root`
directory. Use a task-owned timestamped destination and avoid deleting shared
storage:

```bash
RUN=/root/task263_qwen_aime_v11_base_load_planner_sanity_s1/run_<UTC>
mkdir -p "$RUN"
rsync -a --exclude .git /work-agents/intern_nemotron_worker_2/Nemotron/ "$RUN/Nemotron/"
```

Any actual smoke launch still requires task262 data readiness and lead
clearance.

### Data/Packing Gate Template

Task262 must publish a manifest and a verification command equivalent to:

```bash
python <task262_verify_script.py> \
  --blend <v11_packed_qwen>/blend.json \
  --metadata <v11_packed_qwen>/splits/metadata.json \
  --exposed-splits <v11_packed_qwen>/splits \
  --fail-on-missing-intended-shards \
  --fail-on-basename-collision \
  --write-report <task262_output>/v11_split_sidecar_report.json
```

Required pass conditions:

- intended and exposed train rows/tokens/shards match, or the pipeline fails
  closed before training;
- hard-math and final-answer sources are decontaminated non-heldout sources;
- AIME2025 prompts/labels appear only as held-out eval/decontamination evidence.

### Base-Load And Nonzero-LR Gate Template

Task263 must publish either an explicit Megatron checkpoint-load proof or a
Bridge-approved HF import proof. Logs must fail closed if all acceptable proof
patterns are absent.

```bash
rg -n 'successfully loaded checkpoint|Bridge-approved HF import|checkpoint.load|load_main_params_from_ckpt|learning rate|nan|inf' <task263_logs>
```

Required pass conditions:

- positive base-load/import proof before SFT;
- no raw-HF-as-Megatron-root silent continuation;
- first logged train step has nonzero LR;
- no random-init-scale first loss/PPL trigger;
- no NaN/Inf trigger;
- configured iterations can consume the intended V11 split at least once.

### Non-AIME Canary And Retention Gate Template

Task264 must publish canary prompt source and hashes, plus an artifact retention
schema.

```bash
sha256sum <task264_canary_prompt_file>
rg -n 'AIME|aime2025|opencompass/AIME2025' <task264_canary_prompt_file>
jq -e '.full_completion or .debug_transcript' <future_eval_results_or_schema>
```

Required pass conditions:

- canary prompts are synthetic, non-AIME, and not train rows;
- canary requires coherent text plus short numeric/final-answer style response;
- future AIME artifacts retain full completions or deterministic debug
  transcripts sufficient for parser-vs-generation forensics.

### Same-Harness AIME Comparison Template

Use task243/task247 corrected protocol only after stages 1-5 pass:

```bash
python3 /root/<task>/eval/run_corrected_math_full_eval.py \
  --aime-score-cache /root/task247_qwen_aime2025_qwen4b_base_smoke_s1/input/aime_score_cache.opencompass_a6ad95f.db \
  --hmmt-output-jsonl /root/<task>/input/not_used_hmmt.jsonl \
  --output-dir /root/<task>/eval/<candidate_ft_aime2025_30x1> \
  --endpoint-url http://127.0.0.1:<port>/v1/chat/completions \
  --model-id <served-v11-ft-model-id> \
  --tasks aime25 \
  --aime-prompt-variant original \
  --aime-max-tokens 8192 \
  --aime-limit-rows 30 \
  --parallelism 4 \
  --timeout 900
```

The comparison is valid only when the base and FT runs use the same cache,
prompt variant, endpoint route, sampling parameters, parser, and all-request
denominator. Parsed rate is diagnostic; the gate is exact-normalized accuracy.

## Required Artifacts By Upstream Task

### task262

Required before stage 1 PASS:

- task262 branch/head/PR or mailbox blocker;
- V11 packed root path;
- `blend.json`, `splits/metadata.json`, shard summary, and generated manifest
  hashes;
- intended-vs-exposed row/token/shard table;
- collision check log;
- sidecar source paths, row counts, checksums;
- decontamination evidence against AIME25/HMMT/MATH heldouts;
- no-AIME-train-data confirmation.

### task263

Required before stage 2 PASS:

- task263 branch/head/PR or blocker;
- Qwen3-4B base file hashes;
- import/checkpoint-load proof log;
- abort-check script/config and log;
- schedule manifest showing nonzero first-step LR and enough iterations;
- NemTron `/root/<task>/run_<UTC>` sync path;
- resource shape, limited to Qwen3-4B and lead-cleared bounded smoke.

### task264

Required before stage 3 PASS:

- task264 branch/head/PR or blocker;
- canary prompt file path and sha256;
- non-AIME/non-train proof for canary prompts;
- config/tokenizer/generation parity checklist;
- retention schema requiring full completions or deterministic debug transcript;
- same-harness gate statement preserving `FT >= 11/30`.

### task265

Required before stages 4-6 PASS:

- task265 branch/head/PR or blocker;
- exact task262/task263/task264 heads reviewed;
- contamination verdict;
- regression/gate verdict;
- approve/request-changes/block matrix;
- residual risks and unreviewed surfaces.

## Residual Risks

- task262/task264 published remote branches currently contain acceptance docs
  only; no actionable artifacts or review reports are present.
- task263 had no visible remote branch/PR during this review, so base-load and
  nonzero-LR gates have no published evidence.
- task265 remote branch is unchanged from `origin/main`; no independent review
  matrix is visible.
- Worker-local dirty or in-progress files in other workspaces are not treated as
  accepted evidence because they are not published exact heads.
- The runbook cannot prove future V11 correctness. It only defines the evidence
  needed before lead can permit the next bounded Qwen3-4B stage.

## Final Gate State

| Decision | Status |
|---|---|
| task266 runbook/repro gate | PASS as static documentation |
| V11 data/packing ready | HOLD/BLOCK |
| V11 base-load/import ready | HOLD/BLOCK |
| V11 non-AIME canary ready | HOLD |
| Bounded Qwen3-4B pilot allowed | NO-GO |
| Same-harness AIME comparison allowed | NO-GO |
| Promotion or 30B/8-GPU | NO-GO |

No stage should move past HOLD until the missing upstream artifacts are
published and independently reviewed at exact branch heads.
