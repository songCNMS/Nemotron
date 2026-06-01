# task260 task255 AIME2025 failure forensics report

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_3,SESSION=1 -->

## Summary

- Task: `task260_qwen_aime_v10_task255_eval_failure_forensics_s1`
- Worker branch:
  `intern_nemotron_worker_3/task260_qwen_aime_v10_task255_eval_failure_forensics_s1`
- PR: pending at report-authoring time
- Scope: read-only forensic comparison of existing task257 FT AIME2025 outputs
  against accepted task247 Qwen3-4B base outputs.
- Main finding: task255 FT failure is generation degeneration/corruption across
  all 30 rows, not an evaluator-only parser or final-answer-format issue.
- Gate state: global `NO-GO/HOLD` remains. This report makes no promotion,
  go/no-go pass, 30B/8-GPU, or training claim.

The FT run produced `0/30` exact-normalized accuracy and `0/30` parsed. Every
FT row has null `prediction`, no `boxed_values`, and no visible final-answer
marker in the preserved `response_tail`. The accepted base under the same
protocol produced `23/30` parsed, `23/30` boxed, and `11/30` correct.

## Artifacts Inspected

FT artifact root:

`/work-agents/intern_nemotron_worker_3/outputs/task257_qwen_aime_v10_task255_same_harness_eval_s1/ft_eval/task255_ft_aime2025_30x1_20260601T204900Z/`

- `summary.json` sha256:
  `ba3dd7b10af3fbafd678df434602b3bee0e829a357025e38e5109cbed7367e6e`
- `results.jsonl` sha256:
  `e4d4ba6ece47e0dff6693066488ebba7461fd12fb8ad6dc26741bb931030f5e6`
- `endpoint_model_manifest.json` sha256:
  `710bb2db20296762ebb6951db566abfcab90bb406e10ef7b2b548fead06f35d9`
- `command.txt` sha256:
  `e82f9f50e2aaad46d7aa54334ab422022c2d45444aa13ec13114ad4968bb902d`
- endpoint log sha256:
  `1011e6c3b373455ca9b7a9a3a87443139a87e581e7daf6d8c966b38551e949b7`
- Row count: 30.

Base artifact root:

`/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z/`

- `summary.json` sha256:
  `376f189c69a8b13fc7752f2f8c362a734154d43fe717209dedf6d0d1649d8639`
- `results.jsonl` sha256:
  `c24ce2bd4b798b0f5913df1a86a34684315a6ac38e3b19764d0dd75889d43961`
- `endpoint_model_manifest.json` sha256:
  `4f17b1b5880e0cfc5697f99df942f31270e9ce5539212cc5494e9034c86ff354`
- `command.txt` sha256:
  `bd60cbb4b0ae65ba7cf549e5cde65142d55f9b2dc62181103e75657a937eff40`
- Source AIME cache sha256:
  `c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74`
- Source manifest sha256:
  `0c68142e83da11107e5dbaa86bfad1dbba87799354853de196c5f2434139b171`
- Row count: 30.

Context reports:

- task255 export report sha256:
  `3893af84bfdb4d78c4f31074a8454b2fa2bab2d69cfec71c42a36b75c49e7686`
- task257 merged report sha256 at this branch:
  `3e7b46e3ab40e8945d3fad127094f3bee5795f082f20e39f298a22f8aa4f6a05`

## Protocol Match

The FT and base commands differ by model, endpoint, and task-owned paths, but
the compared evaluator settings match:

- task: AIME2025 only, `30x1`
- prompt variant: `original`
- route: `/v1/chat/completions`
- max tokens: `8192`
- temperature: `0.0`
- top_p: `0.00001`
- parallelism: `4`
- timeout: `900`
- denominator: exact-normalized all 30 requests
- endpoint shape: no reasoning parser; `message.content` route

This makes an evaluator/protocol mismatch an unlikely primary cause.

## Evidence Limit

The inspected `results.jsonl` rows do not preserve full completion bodies.
They preserve row metrics, `prediction`, `boxed_values`, `response_chars`,
usage, finish reason, and a 1200-character `response_tail`. The endpoint log is
a server progress log and does not contain full raw completions. The matrix
below therefore classifies the preserved tail plus structured row fields. This
is still enough to explain the `0/30` parse collapse because every row has null
`prediction`, no boxed value, and no final-answer marker in the preserved tail.

## Per-Problem Failure Matrix

Tags:

- `L`: FT stopped by max-token length.
- `S`: FT stopped naturally.
- `NB`: no boxed value.
- `NP`: null prediction.
- `NF`: no final-answer marker in preserved tail.
- `MS`: mixed-script tail noise.
- `CA`: code/API-like tail tokens.
- `REP`: repeated tail pattern.

| id | exp | FT finish/tok | FT tags | base parsed/correct finish/tok |
|---|---:|---|---|---|
| aime_01_r01 | 70 | S/6771 | NB NP NF MS CA REP | 1/1 stop/962 |
| aime_02_r01 | 588 | L/8192 | NB NP NF MS CA REP | 1/0 stop/7226 |
| aime_03_r01 | 16 | S/2267 | NB NP NF MS CA REP | 1/1 stop/1271 |
| aime_04_r01 | 117 | L/8192 | NB NP NF MS CA REP | 1/1 stop/2092 |
| aime_05_r01 | 279 | L/8192 | NB NP NF MS CA REP | 1/1 stop/5277 |
| aime_06_r01 | 504 | L/8192 | NB NP NF MS CA REP | 1/1 stop/2001 |
| aime_07_r01 | 821 | S/1409 | NB NP NF MS REP | 1/0 stop/5101 |
| aime_08_r01 | 77 | L/8192 | NB NP NF MS | 1/0 stop/7405 |
| aime_09_r01 | 62 | L/8192 | NB NP NF MS REP | 0/0 length/8192 |
| aime_10_r01 | 81 | L/8192 | NB NP NF MS CA REP | 1/0 length/8192 |
| aime_11_r01 | 259 | L/8192 | NB NP NF MS CA REP | 0/0 length/8192 |
| aime_12_r01 | 510 | L/8192 | NB NP NF MS CA REP | 1/1 stop/5422 |
| aime_13_r01 | 204 | L/8192 | NB NP NF MS REP | 1/0 stop/7929 |
| aime_14_r01 | 60 | L/8192 | NB NP NF MS CA REP | 1/0 stop/6793 |
| aime_15_r01 | 735 | L/8192 | NB NP NF MS REP | 0/0 length/8192 |
| aime_16_r01 | 468 | S/5468 | NB NP NF MS CA REP | 1/1 stop/1479 |
| aime_17_r01 | 49 | L/8192 | NB NP NF MS CA | 1/1 stop/2138 |
| aime_18_r01 | 82 | L/8192 | NB NP NF MS REP | 0/0 length/8192 |
| aime_19_r01 | 106 | L/8192 | NB NP NF MS CA REP | 1/0 stop/1731 |
| aime_20_r01 | 336^\\circ | L/8192 | NB NP NF MS CA REP | 1/0 stop/7620 |
| aime_21_r01 | 293 | S/3312 | NB NP NF MS CA REP | 0/0 length/8192 |
| aime_22_r01 | 237 | L/8192 | NB NP NF MS CA | 1/0 stop/2774 |
| aime_23_r01 | 610 | L/8192 | NB NP NF MS CA REP | 1/0 stop/5773 |
| aime_24_r01 | 149 | S/3074 | NB NP NF MS CA REP | 1/1 stop/3688 |
| aime_25_r01 | 907 | L/8192 | NB NP NF MS CA REP | 1/0 length/8192 |
| aime_26_r01 | 113 | L/8192 | NB NP NF MS CA REP | 1/1 stop/6677 |
| aime_27_r01 | 19 | L/8192 | NB NP NF MS CA REP | 1/1 stop/6881 |
| aime_28_r01 | 248 | S/5356 | NB NP NF MS CA REP | 1/0 stop/7820 |
| aime_29_r01 | 104 | L/8192 | NB NP NF MS CA REP | 0/0 length/8192 |
| aime_30_r01 | 240 | L/8192 | NB NP NF MS CA REP | 0/0 length/8192 |

## Aggregate Failure Clusters

FT aggregate:

- `30/30` requests returned status ok.
- `0/30` parsed, `0/30` correct, exact-normalized accuracy `0.0`.
- `0/30` rows have a non-null prediction.
- `0/30` rows have boxed values.
- `0/30` rows have a visible final-answer marker in preserved tail.
- `23/30` rows hit length stop at 8192 completion tokens.
- `7/30` rows stopped naturally, but still had null prediction and no final
  answer evidence.
- `30/30` preserved tails contain mixed-script noise.
- `24/30` preserved tails contain code/API-like tokens.
- `27/30` preserved tails contain repeated patterns.
- Average completion tokens: `7202.433333333333`; median: `8192`.

Base aggregate:

- `30/30` requests returned status ok.
- `23/30` parsed, `11/30` correct, exact-normalized accuracy
  `0.36666666666666664`.
- `23/30` rows have boxed values.
- `21/30` rows stopped naturally; `9/30` hit length.
- Average completion tokens: `5726.266666666666`; median: `6837`.
- Base-correct sample ids: `aime_01_r01`, `aime_03_r01`, `aime_04_r01`,
  `aime_05_r01`, `aime_06_r01`, `aime_12_r01`, `aime_16_r01`,
  `aime_17_r01`, `aime_24_r01`, `aime_26_r01`, `aime_27_r01`.

## Base Comparison

The base model demonstrates that the task247/task257 harness can produce
normal mathematical completions and parse final answers under the same
settings. On every problem where the base was correct, the FT row still had
null prediction, no boxed value, no final marker, and mixed-script tail noise.

The collapse is therefore upstream of scoring. The parser did not miss a
well-formed answer; it received no answer-like field to parse. The high length
stop rate is a symptom, not the full failure: seven FT rows stopped naturally
and still contained no parseable final answer.

## Ranked Root-Cause Hypotheses

1. **Exported FT model or checkpoint is functionally corrupted or incompatible
   with Qwen3-4B inference.** Evidence: all 30 outputs collapse into
   mixed-script/code-token streams while the base model under the same harness
   remains parseable on 23/30. This is stronger than ordinary overfitting or
   answer-format drift.
2. **Training/export tensor mapping, tokenizer, or chat-template parity is
   broken for the task255 artifact.** Evidence: the endpoint serves
   `message.content` and does not fail structurally, but content is not
   language-model coherent. This points to model artifact semantics rather than
   HTTP route or parser shape.
3. **The one-iteration V10 training command or packed-data objective caused a
   destructive update.** Evidence: task255 used a tiny one-iteration pilot
   over reviewed packed data. A normal small SFT step should not erase base
   generation this completely, so this remains plausible mainly if loss
   masking, sequence packing, optimizer state, or checkpoint loading was wrong.
4. **Evaluator/prompt/parser mismatch.** Low likelihood. The task247 base run
   used the same evaluator settings and parsed 23/30; task257 endpoint manifest
   also records the expected no-reasoning-parser content path.
5. **Final-answer formatting only.** Very low likelihood. The FT rows do not
   merely omit `\\boxed{}` around plausible math answers; the preserved tails
   are mixed-script/code-token noise and `prediction` is null for every row.

## V11 Recommendations

1. Treat task255 V10 as a failed/no-promotion artifact. Do not use it as the
   starting point for scale-up or 30B/8-GPU work.
2. Before any V11 AIME comparison, make task255/task258 artifact evidence
   reviewer-readable: exact checkpoint/HF export paths, config/tokenizer files,
   safetensor hashes, and a reproducible manifest that a reviewer can inspect.
3. Add a non-AIME export-load canary before same-harness AIME eval. Use simple
   synthetic prompts that are not AIME2025 and are not train data, then require
   coherent text and a short numeric answer from the exported FT model.
4. Add artifact sanity checks before eval: tokenizer/chat-template parity with
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`, special-token
   ids, generation config, layer shape checks, NaN/Inf scan, and selected layer
   norm deltas versus base and checkpoint.
5. If V11 trains again, first run a dry-run or one-step pilot with saved
   pre/post non-AIME generation canaries, training loss, gradient norm, and
   checkpoint/export load checks before any held-out AIME run.
6. Improve future eval artifact retention by storing full completions or a
   larger deterministic debug transcript alongside `response_tail`; this is for
   forensic audit only and should not become training data.

## Boundary Confirmation

- No new AIME/task243 eval was run.
- No endpoint was launched.
- No training or export was run.
- No code or existing artifact was modified.
- AIME2025 prompts/labels were not used as trainable data.
- No promotion, go/no-go pass, 30B/8-GPU, or scale-up claim is made.
- No shared deletion or overwrite was performed.
