# task273 Qwen AIME V11 eval gate continuity report

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_3,SESSION=1 -->

## Summary

- Task: `task273_qwen_aime_v11_eval_gate_continuity_s1`.
- Branch:
  `intern_nemotron_worker_3/task273_qwen_aime_v11_eval_gate_continuity_s1`.
- Base reviewed: `origin/main` at
  `958c283813960d90749d51c8880354b89caa7ff8`.
- Lead docs source:
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at
  `b7e58017ce2324ef24bf130e7ad84082b5271d1f`.
- Decision: `APPROVE/PASS` for eval-gate continuity documentation. The
  canonical comparator and prerequisites are unambiguous.
- Global Qwen AIME disposition remains `NO-GO/HOLD`: no V11 FT checkpoint,
  same-harness FT-vs-base AIME artifact, promotion clearance, live task243 eval
  clearance, or 30B/8-GPU clearance exists.

Session 40 changes only the prior runtime-route picture for no-training
Qwen3-4B Bridge import/preflight proof. It does not create an FT artifact and
does not authorize AIME/task243 eval, training, export, promotion, AIME2025
train data, or scale-up.

## Evidence Inspected

- Gate config:
  `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_aime2025_base_vs_ft_gate.yaml`.
- Accepted base report:
  `workspace/tasks/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_smoke_report.md`.
- V10 same-harness failure:
  `workspace/tasks/task257_qwen_aime_v10_task255_same_harness_eval_s1/task255_same_harness_eval_report.md`.
- V10 forensics and root cause:
  `workspace/tasks/task260_qwen_aime_v10_task255_eval_failure_forensics_s1/task260_failure_forensics_report.md`
  and
  `workspace/tasks/task261_qwen_aime_v10_task255_data_training_root_cause_s1/task255_data_training_root_cause_report.md`.
- V11 static canary/retention gate:
  `workspace/tasks/task264_qwen_aime_v11_eval_gate_canary_retention_s1/v11_canary_retention_report.md`.
- V11 runbook and runtime blocker lineage:
  `workspace/tasks/task266_qwen_aime_v11_runbook_repro_gate_s1/v11_runbook_repro_gate_report.md`,
  `workspace/tasks/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/runtime_probe_report.md`,
  and
  `workspace/tasks/task270_qwen_aime_v11_nemtron_runtime_route_audit_s1/nemtron_runtime_route_audit_report.md`.
- GitHub PR state for the merged blocker/runbook records:
  #337 merged at `8fb1a1cb042fca0a0ca3491363fb0e5616909010`,
  #338 merged at `8d4382b6572b91ec2ca27876cd0f961deb7c2f81`,
  and #339 merged at `958c283813960d90749d51c8880354b89caa7ff8`.
- Lead Session 71 task split on the docs branch, which records the coordinator
  Session 40 runtime-unblock report and assigns task271-task275.
- Coordinator Session 40 evidence root, inspected read-only:
  `/work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z`.
- Stale task243 closeout PR #322: `CLOSED`, unmerged, `DIRTY`, head
  `f7cc324599b4ffdf4310fc792548ed466e3d3b19`.

## Canonical Baseline

The accepted same-harness Qwen3-4B base comparator remains:

- Model path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Artifact root:
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z`.
- Input cache:
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache/aime_score_cache.opencompass_a6ad95f.db`.
- Cache sha256 from task257/task260:
  `c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74`.
- Source dataset revision:
  `opencompass/AIME2025@a6ad95f611d72cf628a80b58bd0432ef6638f958`.
- Score: `11/30`, exact-normalized accuracy
  `0.36666666666666664`.
- Request status: `30/30 ok`.
- Parsed count: `23/30`.
- Finish reasons: `stop=21`, `length=9`.
- Base artifact hashes:
  `summary.json`
  `376f189c69a8b13fc7752f2f8c362a734154d43fe717209dedf6d0d1649d8639`,
  `results.jsonl`
  `c24ce2bd4b798b0f5913df1a86a34684315a6ac38e3b19764d0dd75889d43961`,
  `command.txt`
  `bd60cbb4b0ae65ba7cf549e5cde65142d55f9b2dc62181103e75657a937eff40`,
  and `endpoint_model_manifest.json`
  `4f17b1b5880e0cfc5697f99df942f31270e9ce5539212cc5494e9034c86ff354`.

The pilot protocol is fixed by task243/task247/task264:

- AIME2025 `30 x 1` pilot, original prompt variant.
- OpenAI chat-completions route `/v1/chat/completions`.
- Qwen checkpoint tokenizer chat template with `enable_thinking=false` and
  `truncate_history_thinking=false`.
- `max_tokens=8192`, `temperature=0.0`, `top_p=1e-5`.
- Parser: boxed-answer or symbolic-final-answer parser.
- Scorer: exact-normalized boxed or symbolic answer match.
- Denominator: all request rows, including unparsed, length-capped, and error
  rows.
- Parsed rate is diagnostic only. The non-regression rule is FT
  exact-normalized accuracy `>= 11/30`.

If any future comparison changes the cache, prompt, runner, parser, endpoint
shape, tokenizer template, sampling settings, or denominator, the base must be
rerun under that exact changed protocol before the FT can be judged.

## Session 40 Runtime Proof Continuity

Lead Session 71 records coordinator Session 40 evidence that
`nemo-toolkit==2.7.3` was installed on NemTron user site and a no-training
Qwen3-4B Bridge import plus fail-closed preflight was run from fresh
`origin/main` sync. The coordinator evidence root is:

`/work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z`

Observed local files and direct sha256 values:

- `logs/symbol_preflight.log`:
  `bfa15c5b26849ef2c802c03b0303d57ada11922c4872068bd17de2c7d0081534`.
- `logs/bridge_import_probe.log`:
  `170b51d0c846c374a82badf780d478d64a946d3131cdc7032808d7c53db21756`.
- `logs/fail_closed_preflight.log`:
  `60db59059560304dc18a6e28498f6be1a08cbc24c26abd6e82241f6e1729c440`.
- `remote_checkpoint_manifest.txt`:
  `51b4ab937a5be23f1391cddd5c5c1425a3f8860e84fe81827fc5ebdee2afb522`.
- `remote_run.txt`:
  `2abbfd1bd76316bfe1b48df0a1f14837847c96de66b18d11f0601a689ff6fe87`.
- `artifact_inventory.sha256`:
  `9526d498c3daa55cee998c38dbde0f7e6ad96b6d2adb133d75bb2141c2e14609`.

Pass markers observed:

- `TASK270_RUNTIME_SYMBOL_PREFLIGHT=PASS`.
- `IMPORT_DONE`.
- `BRIDGE_IMPORT_RC=0`.
- `TASK270_FAIL_CLOSED_PREFLIGHT=PASS`.

The remote run path is:

`/root/task_coordinator_nemotron_coordinator_06b9acba/session40_nemo_install_probe_20260602T015146Z`

The imported checkpoint root is:

`/root/task_coordinator_nemotron_coordinator_06b9acba/session40_nemo_install_probe_20260602T015146Z/qwen3_4b_bridge_import_iter0`

The manifest reports size `7.5G`, `latest_checkpointed_iteration.txt`,
`iter_0000000`, two `.distcp` shards, tokenizer files, and NeMo package
metadata for `nemo-toolkit` version `2.7.3`.

Residual proof issues: `sha256sum -c session40_evidence.sha256` validates the
main logs and checkpoint manifest but reports `artifact_inventory.sha256:
FAILED` because `session40_evidence.sha256` records the empty-file hash for
that inventory while the current inventory file is non-empty. The symbol
preflight log also prints `megatron=None` while `megatron.bridge` is importable
and the pass marker is present. These do not affect the AIME baseline
continuity decision, but task271 should reconcile them when deciding whether
the Session 40 proof is independently accepted.

Continuity interpretation:

- Session 40 can clear only the prior runtime-route blocker for a no-training
  Bridge import/preflight proof after task271/lead acceptance.
- It is not training evidence, an export-load canary, an FT checkpoint, an
  AIME/task243 result, or a promotion result.
- Task272 planning and any later lead clearance are still required before a
  bounded Qwen3-4B V11 pilot action.

## Continuity Matrix

| Surface | Current evidence | Continuity status |
|---|---|---|
| Base comparator | task247 accepted Qwen3-4B base `11/30` with same-harness artifact hashes | Ready as the canonical pilot comparator |
| Gate config | task243/task264 config requires base score, `FT >= base`, all-request denominator, non-AIME canary, retention schema | Ready as static gate definition |
| V10/task255 FT | task257 result `0/30`, parsed `0/30`; task260/task261 identify corrupted/random-like generation and likely load/training defects | Failed/stale; not reusable for promotion or as a V11 candidate |
| Data/packing repair | task262 static repair evidence is summarized by task266 and merged via #336 | Static repair evidence exists; future candidate still needs accepted data-safety/readiness review |
| Pre-AIME canary | task264 static canary and retention schema merged via #335 | Static gate exists; no future V11 candidate has passed it |
| Runtime route | task268/#338 and task270/#339 recorded blocker; coordinator Session 40 later reports positive no-training Bridge import/preflight evidence | Runtime blocker may be cleared only after task271/lead acceptance; not an AIME clearance |
| Future V11 FT artifact | No accepted V11 FT checkpoint/export exists | Missing |
| Same-harness FT-vs-base AIME | No V11 FT AIME artifact exists | Not allowed yet |
| Promotion / 30B / 8-GPU | No lead clearance and no non-regression evidence | `NO-GO/HOLD` |

## Prerequisites For Future FT-vs-Base Comparison

Before any future V11 FT checkpoint can be judged against the accepted base:

1. Task271 and lead must accept or explicitly clear the Session 40 Bridge
   import/preflight proof, including the checksum-sidecar and symbol-log issues.
2. Task272 or equivalent lead-approved planning must define the bounded
   no-training-to-pilot route and exact artifact paths.
3. A new V11 Qwen3-4B FT candidate must exist as a reviewer-readable artifact:
   checkpoint/export path, config/tokenizer files, safetensor or distcp hashes,
   model provenance, launch command, and manifest.
4. The candidate must not reuse task255/V10 failed artifacts and must not use
   AIME2025 prompts or labels as trainable data.
5. V11 data/packing and contamination/regression reviews must not be blocking.
6. The task264 non-AIME export-load canary must pass on the exact candidate
   artifact before AIME/task243 evaluation is requested.
7. The AIME artifact must retain `summary.json`, `results.jsonl`,
   `command.txt`, `endpoint_model_manifest.json`, `full_completions.jsonl`, and
   `completion_retention_manifest.json`, with retained completions marked
   review-only and not trainable data.
8. The FT AIME run must use the same cache, runner, prompt variant, endpoint
   route, tokenizer template, sampling, parser, and all-request denominator as
   the accepted base. If not, rerun the base under the exact same protocol
   before judging FT.
9. The pilot non-regression threshold is FT exact-normalized AIME2025
   `>= 11/30 = 0.36666666666666664`. A lower score is FAIL/no promotion. A
   parsed-rate change alone is diagnostic, not a pass/fail rule.
10. No promotion, full protocol, 30B/8-GPU, or scale-up action is allowed
    without a separate lead gate after the same-harness evidence exists.

## Stale Or Non-Reusable Evidence

- PR #322 is closed unmerged and was dirty; it was old post-#319 task243
  closeout metadata only and is superseded by task247, task257, task260, and
  later V11 gate evidence.
- task255/V10 output is a failure artifact only: same-harness FT `0/30` below
  base `11/30`, with no promotion claim.
- task268/#338 and task270/#339 remain useful as runtime-blocker history, but
  their blocker disposition is superseded only for the narrow Bridge
  import/preflight route if task271 accepts Session 40 proof.
- Any worker-local, mailbox-only, or unmerged artifact that lacks exact path,
  hashes, and reviewer-readable provenance is not valid for the FT-vs-base gate.

## Checks

- `git diff --check`: passed.
- ASCII scan over task273 docs and worker_3 status: passed.
- No code, artifacts, endpoints, training, export, live AIME/task243 eval, or
  shared storage writes were performed for this review.

## Boundary Confirmation

- No live AIME/task243 eval was run.
- No endpoint was launched.
- No training, export, nonzero-LR smoke, or model modification was run.
- No AIME2025 prompt or label was used as trainable data.
- No task255 artifact was reused as a candidate.
- No promotion, go/no-go pass, 30B/8-GPU, or scale-up clearance is claimed.
- No main push, merge, or shared deletion/overwrite was performed.
