# task314 MMLU-Pro regression forensics report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_1,SESSION=90 -->

Generated: 2026-06-03T19:20:00Z

## Disposition

Recommendation: `APPROVE_FORENSICS`.

Task311's gate disposition should remain
`FAIL_MMLU_PRO_BELOW_BASE_WITH_AIME_HMMT_PASS`. I found no row-alignment,
prompt-hash, parser, endpoint-protocol, status, stop-reason, or checksum issue
that explains the MMLU-Pro `-2` delta as an evaluator artifact. The evidence
points to real answer-choice drift between the base and task310 FT models under
the same corrected-Qwen MMLU-Pro protocol.

This report does not authorize promotion, new training, new eval rows, export,
endpoint launch, task255 reuse, AIME2025 train data, shared deletion, main push,
merge, 30B scale action, or 8-GPU use.

## Reviewed target

| Item | Value |
|---|---|
| Worker branch | `intern_nemotron_worker_1/task314_qwen_all_sft_mmlu_pro_regression_forensics_s1` |
| Base branch point | `origin/main` `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb` |
| Lead docs source | `origin/intern_nemotron_lead/session1-recovery-task-docs` `f1f5efab8c425077033bcceeeef14062ea87d7c9` |
| Task311 PR target | #371 |
| #371 state checked | `OPEN`, base `main`, `CLEAN`, non-draft |
| #371 exact head reviewed | `9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6` |
| Task311 source head in eval manifests | `1ce85c6382d0587a35ab02830c0d08b7c874c5b3` |

## Artifact roots

| Role | Path |
|---|---|
| Base MMLU-Pro | `/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/eval/corrected_qwen/base_mmlu_pro_task311_20260603T183600Z` |
| FT MMLU-Pro | `/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/eval/corrected_qwen/ft_mmlu_pro_task310_20260603T184300Z` |
| Task314 analysis output | `/work-agents/intern_nemotron_worker_1/outputs/task314_qwen_all_sft_mmlu_pro_regression_forensics_s1/run_20260603T191500Z` |

Base model:
`qwen3-30b-a3b-instruct-2507-base-task311`.

FT model:
`task310-qwen3-30b-a3b-all-sft-iter0000035`.

## Source checksum review

All result-bearing source artifacts matched their task311 checksum manifests:
`results.jsonl`, `full_completions.jsonl`, `parser_diagnostics.jsonl`,
`summary.json`, `manifests/mmlu_pro_row_manifest.jsonl`,
`manifests/command_env_manifest.json`, and `manifests/endpoint_manifest.json`.

| Role | File | sha256 |
|---|---|---:|
| Base | `checksum_manifest.json` direct | `c9d2c51b8c9764c16e6829f972232ef5fc9ba9646ab94c8e73e916fde4a9e634` |
| Base | `results.jsonl` | `8f6a48da6d113ee3e1ecda3f07e4814fd190e6e412a60da9dcef23605f1e8f84` |
| Base | `parser_diagnostics.jsonl` | `e4f2c1ece115b51c010df897812859b3de6b526988cdeb55fb8369b4590cf3cb` |
| Base | `full_completions.jsonl` | `aa1b3c7a2990a349e97aa952c74fad46f2c33636e1f7639f6284b0b03fef3b2e` |
| Base | `summary.json` | `fe2247bd2a861f8c327f652211b8d7b52b4ec8a4f4115242cbb839e72975a917` |
| Base | `manifests/mmlu_pro_row_manifest.jsonl` | `d6506bc08cb51f77ef1572a5546db0e19a146a49d936dcf07cf160e341fda985` |
| FT | `checksum_manifest.json` direct | `15ad874abe1bbb18067207793a575755df9d5b3cf479a3e6525a86718e0b154e` |
| FT | `results.jsonl` | `4a8c61a02f4bb05be61f47d746aab29640413432479d40a0ce76232fe9551f69` |
| FT | `parser_diagnostics.jsonl` | `f5b4cc3c4a5b8f2b877f51eeec7dd16d973e4d27591cfc8f65095a13d70cbc40` |
| FT | `full_completions.jsonl` | `5ba142d797e4245ade0a08f3e0121ca6caa112eddd6593d367f46786060ed54a` |
| FT | `summary.json` | `0d6b12f55e350584fa9f198273173292060bdcef1da3998618eaca354f8d0108` |
| FT | `manifests/mmlu_pro_row_manifest.jsonl` | `d6506bc08cb51f77ef1572a5546db0e19a146a49d936dcf07cf160e341fda985` |

Residual checksum note: direct `logs/run.log` hashes differ from the manifest
entries because `summary.json` was appended after the manifest-sized log prefix.
For both base and FT, the prefix hash matches the manifest entry and the suffix
bytes equal `summary.json` exactly:

| Role | Manifest log sha | Direct log sha | Prefix/suffix result |
|---|---:|---:|---|
| Base | `1f03f8cb7ed1643056a40999158120814829550c3e2d7f44f0d13007c6ee2035` | `3c5f7bd2de23752b518431b3663c8668dafa8df1948a2e0b32cd3005a3f90b62` | PASS: prefix matches, 4252-byte suffix equals `summary.json` |
| FT | `394bb9d73c29fdae2441b93084bdd0dfbec4e3fda7c5c6f16878d4e50e2edef0` | `c117d60b6a4c1cb425eac8b248c621ae3a6fd3ece71c916e6b842f19a0cc5d12` | PASS: prefix matches, 4436-byte suffix equals `summary.json` |

## Protocol and row alignment

| Check | Result |
|---|---|
| Base rows / FT rows | `12032 / 12032` |
| Same result `sample_id` set | PASS |
| Same result `sample_id` order | PASS |
| Same row manifest set and order | PASS |
| Base/FT prompt sha mismatches | `0` |
| Base/FT problem sha mismatches | `0` |
| Base/FT expected-answer mismatches | `0` |
| Base/FT category mismatches | `0` |
| Base/FT doc_id mismatches | `0` |
| Result rows match own row manifest hashes | PASS, `0` prompt/problem mismatches in each role |
| Result order equals manifest order | No; both result files share the same order, but it differs from the row-manifest order. Sets and hashes match. |
| Input sha256 | `1c23fc1dae4745edcab672973ef66516cde6ff94f26e59be845a97c072caef36` for both roles |
| Endpoint URL | `http://127.0.0.1:13231/v1/chat/completions` for both roles |
| Protocol | same: `max_tokens=64`, `parallelism=32`, `temperature=0.0`, `top_p=1e-05`, denominator all requested rows |
| Prompt variant | `chat_json_answer_only` |
| Parser | `JSON answer field A-J, then answer-colon fallback, then letter fallback` |

## Overall MMLU-Pro result

| Metric | Base | FT | Delta |
|---|---:|---:|---:|
| Correct rows | `6758` | `6756` | `-2` |
| Rows | `12032` | `12032` | `0` |
| Accuracy | `0.5616688829787234` | `0.5615026595744681` | `-0.0001662234042553168` |
| Parsed rows | `12032` | `12032` | `0` |
| Status counts | `ok: 12032` | `ok: 12032` | none |
| Finish reasons | `stop: 12032` | `stop: 12032` | none |
| Valid JSON answer responses | `12032` | `12032` | none |
| Completion token counts | `6: 12032` | `6: 12032` | none |
| Response char counts | `14: 12032` | `14: 12032` | none |
| Parser errors | `None: 12032` | `None: 12032` | none |

Every response in both runs is the compact JSON shape `{"answer":"X"}`. There
are no unparsable rows, no timeout/status failures, no stop-reason differences,
and no response-length or completion-token signal suggesting parser/protocol
breakage.

## Row transitions

| Transition | Count |
|---|---:|
| Base correct, FT wrong | `92` |
| Base wrong, FT correct | `90` |
| Both correct | `6666` |
| Both wrong | `5184` |

There are `352` rows with changed prediction letters. They account for all
correctness changes and `170` both-wrong answer swaps:

| Changed-prediction group | Count |
|---|---:|
| Base correct, FT wrong | `92` |
| Base wrong, FT correct | `90` |
| Both wrong | `170` |
| Both correct | `0` |
| Same prediction but changed correctness | `0` |
| Same prediction but changed response hash | `0` |

This is the main forensic finding: the net `-2` is the difference between 92
losses and 90 gains, not a row-count, parsing, or denominator issue.

## Category deltas

| Category | Rows | Base correct | FT correct | Delta | Losses | Gains |
|---|---:|---:|---:|---:|---:|---:|
| biology | `717` | `601` | `600` | `-1` | `3` | `2` |
| business | `789` | `369` | `368` | `-1` | `6` | `5` |
| chemistry | `1132` | `469` | `466` | `-3` | `7` | `4` |
| computer science | `410` | `232` | `232` | `0` | `2` | `2` |
| economics | `844` | `611` | `611` | `0` | `6` | `6` |
| engineering | `969` | `464` | `466` | `+2` | `13` | `15` |
| health | `818` | `557` | `553` | `-4` | `6` | `2` |
| history | `381` | `245` | `243` | `-2` | `5` | `3` |
| law | `1101` | `488` | `491` | `+3` | `9` | `12` |
| math | `1351` | `691` | `704` | `+13` | `6` | `19` |
| other | `924` | `518` | `516` | `-2` | `7` | `5` |
| philosophy | `499` | `288` | `288` | `0` | `2` | `2` |
| physics | `1299` | `618` | `612` | `-6` | `16` | `10` |
| psychology | `798` | `607` | `606` | `-1` | `4` | `3` |

The FT model gained most in math (`+13`), law (`+3`), and engineering (`+2`),
but lost enough in physics (`-6`), health (`-4`), chemistry (`-3`), history
(`-2`), other (`-2`), and smaller categories to finish at net `-2`.

## Example row transitions

| Transition | sample_id | doc_id | Category | Expected | Base pred | FT pred |
|---|---|---:|---|---|---|---|
| Loss | `mmlu_pro_02913` | `3031` | biology | `I` | `I` | `C` |
| Loss | `mmlu_pro_03012` | `3132` | biology | `B` | `B` | `A` |
| Loss | `mmlu_pro_00036` | `106` | business | `H` | `H` | `E` |
| Loss | `mmlu_pro_03555` | `3676` | chemistry | `J` | `J` | `D` |
| Gain | `mmlu_pro_02987` | `3106` | biology | `A` | `C` | `A` |
| Gain | `mmlu_pro_03311` | `3432` | biology | `J` | `B` | `J` |
| Gain | `mmlu_pro_00110` | `181` | business | `G` | `I` | `G` |
| Gain | `mmlu_pro_03855` | `3978` | chemistry | `B` | `C` | `B` |

Full row-level tables are in the task314 output root.

## Task314 output checksums

| File | sha256 |
|---|---:|
| `mmlu_pro_forensics_summary.json` | `ad32029db43672fa96cbd722b6beeed4121ce1b8d4e94c0f2fb5d051b61a38c9` |
| `mmlu_pro_row_transitions.jsonl` | `ab338411b96010b3408679f56d42185d69907bfd4a6272c85b8481d3ef077760` |
| `mmlu_pro_changed_predictions.jsonl` | `3a5f3e9c64c96b01bb5ae772c8a758f50e5bdfa32eb878423dfd11bfc5517bb8` |
| `mmlu_pro_category_deltas.json` | `6bad651016a28ef7e1af6a50560108f93093144672f32beec3297062fe09c265` |
| `mmlu_pro_category_deltas.csv` | `dc078a1d583f8ea6748468acb060a8f7137b22c1aa6beec3c5c1a3375fa4849e` |
| `mmlu_pro_transition_examples.csv` | `c0f573e497127b23f8262e2f1ada5d4c9cd32bae8f67949d74d20221fee00517` |
| `output_checksum_manifest.json` | `10bd7713eb6bc82a8fc5b7421115356f93ac95c72f4dc675908c9d941722ba50` |

## Residual risks

1. This is a forensic audit over existing task311 artifacts, not a fresh
   reproducibility run. If lead wants stochastic/retry assurance, that should
   be a separately authorized bounded rerun task.
2. `logs/run.log` direct hashes do not match manifest entries due to appended
   `summary.json`, but the prefix/suffix proof is clean and result-bearing
   files match their manifests directly.
3. The result file order differs from row-manifest order. This does not affect
   the comparison because base and FT result order matches, sample sets match,
   and every prompt/problem/expected/category/doc_id hash check passes.
4. The MMLU-Pro regression is small in net count but broad in row churn:
   `352` changed predictions, `92` losses, and `90` gains.

## Commands and environment

Local host:
`lg-cmc-b7r201-n09u29-cpu-000191`.

Python:
`Python 3.12.3`.

Read-only checks run:

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git checkout -b intern_nemotron_worker_1/task314_qwen_all_sft_mmlu_pro_regression_forensics_s1 origin/main
git checkout f1f5efab8c425077033bcceeeef14062ea87d7c9 -- workspace/tasks/task314_qwen_all_sft_mmlu_pro_regression_forensics_s1
gh pr view 371 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,url
python3 - <<'PY'
# Loaded task311 MMLU-Pro JSONL/manifests, compared rows, and wrote task314
# output tables. No model, endpoint, training, or evaluator command was run.
PY
sha256sum /work-agents/intern_nemotron_worker_1/outputs/task314_qwen_all_sft_mmlu_pro_regression_forensics_s1/run_20260603T191500Z/*
```

No training, packing, new eval rows, export, endpoint launch, promotion,
task255 reuse, AIME2025 train data, shared deletion, product-code edits, main
push, merge, 30B launch, or 8-GPU action was performed.
