# task294 independent review report - task293 AIME gate

<!-- METADATA:STATUS=Complete,ASSIGNEE=intern_nemotron_worker_4,SESSION=1 -->

## Decision

- Decision: `APPROVE_AIME_GATE_PASS_WITH_RESIDUAL`
- Reviewed task293 evidence source head:
  `87de0a97e6c0406a4b67520faab6b11d91d9131e`
- Reviewed task293 PR/report head for closeout consistency:
  `672d0101681a5d9c4b6c34814c75fcc0d97b4fcb`
- Task293 PR: #356
  `https://github.com/songCNMS/Nemotron/pull/356`
- Task294 review PR: #357
  `https://github.com/songCNMS/Nemotron/pull/357`
- Artifact root:
  `/work-agents/intern_nemotron_worker_3/outputs/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1/run_20260602T085237Z`

The task293 artifacts consistently prove a corrected AIME2025 FT-vs-base metric
pass for task285 Qwen3-4B iter2: FT `12/30 = 0.4` versus accepted base
`11/30 = 0.36666666666666664`.

This approval is bounded to AIME metric gate evidence. It does not authorize
export, endpoint, promotion, training, canary/eval reruns, task255 reuse, shared
deletion, 30B, or 8-GPU.

## Read-only checks

- `git fetch origin intern_nemotron_worker_3/task293_qwen_aime_v11_task285_same_harness_aime_eval_s1`
- `gh pr list --state all --search "task293" --json ...`
- `git diff --name-status origin/main...87de0a97e6c0406a4b67520faab6b11d91d9131e`
- `git diff --check origin/main...87de0a97e6c0406a4b67520faab6b11d91d9131e`
- `git diff --name-status 87de0a97e6c0406a4b67520faab6b11d91d9131e..672d0101681a5d9c4b6c34814c75fcc0d97b4fcb`
- `git show` on the task293 runner and official report.
- `sha256sum` on task293 artifacts/logs and accepted task247 base artifacts.
- `jq` on task293 `summary.json`, `results.jsonl`,
  `full_completions.jsonl`, prompt/checkpoint/command manifests, and task247
  base `summary.json`.
- Recomputed every file in task293 `checksum_manifest.json`; all matched.
- Tailed `remote_no_export_aime_eval.log`.

No AIME/eval rerun, training, optimizer step, export, endpoint launch,
promotion, task255 use, shared deletion, main push, merge, 30B, or 8-GPU action
was performed.

## Source and PR scope

The assigned source head `87de0a97e6c0406a4b67520faab6b11d91d9131e` is in the
worker_3 task293 branch history. The current task293 PR #356 head observed
during review is `672d0101681a5d9c4b6c34814c75fcc0d97b4fcb`, OPEN/base
`main`/CLEAN.

The exact source-head diff contains worker_3 status, task293 docs, and the
task-owned runner `run_no_export_aime_eval.py`. The later drift from `87de0a97`
to `672d010` adds the official task293 report and closeout/status metadata; it
does not change the reviewed artifact source head.

`git diff --check` was clean for the assigned source head.

## Artifact checksums

Verified task293 artifact hashes:

| File | sha256 |
|---|---|
| `artifacts/aime_eval/summary.json` | `64a378ca54534ec426b92a7b6bc436edb4fddd2ea1ba831f61afeed4e1ad39b7` |
| `artifacts/aime_eval/results.jsonl` | `4cbc2a9543a658df6a3e18e3128c5a5c9a173f9a575372095cfcbe5d6232aca5` |
| `artifacts/aime_eval/full_completions.jsonl` | `5cb1e11ab8d331127c7c12f2cd8c04d83d2e6bd93445a5ebffc62363e2a818b4` |
| `artifacts/manifests/aime_prompt_manifest.json` | `93146086fcc2214fc3c866354e23358d320377caddb6d2b5a2bd58954e85b919` |
| `artifacts/manifests/checkpoint_load_manifest.json` | `243044f2e548e0c8b1b539e9c11fee17a39b4d45898e1a6601382716e4d90c74` |
| `artifacts/manifests/command_env_manifest.json` | `5b128b5cc84159b8603b07fc92475ebc768152b7c0ea0fae0897c6635a502ccf` |
| `artifacts/manifests/checksum_manifest.json` | `6a47e802433648248658010125db51474d0b4af565dc10c637d004900948e7d4` |
| `logs/remote_no_export_aime_eval.log` | `c0dbfcd93cbb7c615c7f784b201a862e338c4eea23c0faf6d9dd9aa5bdcae4ab` |
| `logs/remote_no_export_aime_eval_command.txt` | `39bfe804e49eb34ada919ef0ec557313a7cea7eed26c86ab18f746cf2fdd487b` |

Verified accepted task247 base hashes:

| File | sha256 |
|---|---|
| `summary.json` | `376f189c69a8b13fc7752f2f8c362a734154d43fe717209dedf6d0d1649d8639` |
| `results.jsonl` | `c24ce2bd4b798b0f5913df1a86a34684315a6ac38e3b19764d0dd75889d43961` |
| `command.txt` | `bd60cbb4b0ae65ba7cf549e5cde65142d55f9b2dc62181103e75657a937eff40` |
| `endpoint_model_manifest.json` | `4f17b1b5880e0cfc5697f99df942f31270e9ce5539212cc5494e9034c86ff354` |
| `aime_score_cache.opencompass_a6ad95f.db` | `c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74` |

## Metric verification

Task293 summary and rows verify:

- disposition: `PASS`
- total requests: `30`
- results rows: `30`
- full completion rows: `30`
- all row status: `ok`
- FT correct rows: `12`
- FT denominator: `30`
- FT exact-normalized accuracy: `0.4`
- accepted base: `11/30 = 0.36666666666666664`
- delta: `+1` correct, `+0.03333333333333338` accuracy
- parsed rows: `21/30`
- finish reasons: `stop=21`, `length=9`
- retained completions: all 30 rows have positive `response_chars` and
  retained `full_text`
- response source: all 30 rows use `request.generated_text`; no
  generated-token detokenization fallback was used.

Correct row ids:
`aime_01_r01`, `aime_03_r01`, `aime_04_r01`, `aime_05_r01`,
`aime_06_r01`, `aime_16_r01`, `aime_17_r01`, `aime_19_r01`,
`aime_21_r01`, `aime_22_r01`, `aime_24_r01`, `aime_27_r01`.

## Same-harness assessment

Accepted same-harness evidence:

- Same AIME score cache sha:
  `c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74`
- Same row count and all-request denominator: `30`
- Same prompt variant: `original`
- Same max token cap: `8192`
- Same parser/normalizer/scorer logic as task247: `boxed_values`,
  `normalize_answer`, exact-normalized `correct`, and `contains_expected`
- Prompt token mismatch count against task247 base: `0`
- Base artifact hashes match accepted task247 base files.

The residual is real and explicitly accepted: `sampling_exact_parameter_match`
is `false` because task247 base used an SGLang `/v1/chat/completions` endpoint
with `temperature=0.0`, `top_p=1e-5`, while task293 FT used the task291-approved
no-export/no-endpoint MCore static engine route with `top_k=1`,
`temperature=1.0`, `top_p=0.0`. I classify this as acceptable for
`APPROVE_AIME_GATE_PASS_WITH_RESIDUAL` because both routes are deterministic
greedy by intent and implementation path, and the prompt tokenization, input
cache, row denominator, max tokens, parser, normalization, and base hashes are
matched. The residual should remain visible in lead gate wording because the
transport and sampling parameter surfaces are not byte-identical.

## Boundary confirmation

Artifact manifests confirm Qwen3-4B only, one visible H200, AIME2025 eval input
only, no AIME2025 train prompts/labels, no training/optimizer, no task255, no
export/conversion, no endpoint launch, no promotion, no shared deletion, no
main push or merge, no 30B, and no 8-GPU.
