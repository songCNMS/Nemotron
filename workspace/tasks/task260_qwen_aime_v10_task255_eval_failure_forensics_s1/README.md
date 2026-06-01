# task260_qwen_aime_v10_task255_eval_failure_forensics_s1 - task255 eval failure forensics

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_3,SESSION=1 -->

## Background

The first Qwen3-4B V10 pilot candidate from task255 failed the corrected
AIME2025 same-harness gate. task257/#330 is merged and records:

- accepted Qwen3-4B base: `11/30 = 0.36666666666666664`;
- task255 FT: `0/30 = 0.0`;
- parsed rows: `0/30`;
- finish reasons: `stop=7`, `length=23`;
- global gate: `NO-GO/HOLD`.

The next improvement step should not train another model blindly. We need a
focused read-only failure analysis of the task255 FT AIME outputs versus the
accepted base outputs.

## Goal

Analyze the task255 FT AIME2025 raw outputs and compare them against the
accepted task247 base outputs to identify why parsing and correctness collapsed,
then recommend concrete next hypotheses for a V11-style fix.

## Scope

- Use task257 FT artifacts:
  `/work-agents/intern_nemotron_worker_3/outputs/task257_qwen_aime_v10_task255_same_harness_eval_s1/ft_eval/task255_ft_aime2025_30x1_20260601T204900Z/`.
- Use accepted task247 base artifacts:
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z/`.
- Compare protocol evidence:
  - AIME2025 30x1;
  - original prompt;
  - `/v1/chat/completions`;
  - max tokens `8192`;
  - temperature `0.0`;
  - top_p `0.00001`;
  - exact-normalized all-request denominator.
- Inspect `summary.json`, `results.jsonl`, `endpoint_model_manifest.json`,
  `command.txt`, and where useful the endpoint log.
- Categorize each of 30 FT outputs:
  - length-stop versus natural stop;
  - answer-format/parser failure pattern;
  - missing final answer marker;
  - repeated text/runaway reasoning;
  - obviously wrong numeric modes if parseable manually;
  - any prompt/template or endpoint-shape anomaly.
- Compare against base outputs for the same problem ids when available.

## Boundaries

- Read-only analysis only.
- Do not train, launch endpoints, run new AIME/task243 eval, alter artifacts,
  modify code, open/merge PRs unless docs/status report is necessary, or claim
  promotion.
- Do not use AIME2025 as trainable data; it remains held-out eval/decontam
  only.
- Do not launch 30B/8-GPU or delete/overwrite shared files under
  `/mnt/cephfs/data/processing/lei.song`.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_3/task260_qwen_aime_v10_task255_eval_failure_forensics_s1`.
- Report file in task docs or output root with:
  - branch/head/PR or mailbox-only status;
  - exact artifacts inspected and hashes;
  - per-problem failure matrix;
  - aggregate failure clusters;
  - comparison to base behavior;
  - likely root-cause hypotheses ranked by evidence;
  - concrete recommendations for the next V11 pilot or blocker if evidence is
    insufficient;
  - boundary confirmation.
- Mailbox report to `intern_nemotron_lead`.

## Acceptance Criteria

- PASS: report explains the `0/30` and `0/30 parsed` failure with enough detail
  to decide next data/training/eval action.
- REQUEST-CHANGES/BLOCK: report identifies missing artifacts or unreadable
  evidence and exact remediation.
- Any conclusion preserves global `NO-GO/HOLD`; no promotion or 30B/8-GPU.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_3`
- Related tasks: task247, task255, task257, task260
- Related PRs: #330, #331
- First gate: read-only failure forensic report.
