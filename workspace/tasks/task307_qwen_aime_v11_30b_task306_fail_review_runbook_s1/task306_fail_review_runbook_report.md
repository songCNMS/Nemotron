# task307 task306 30B fail review and runbook report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_4,SESSION=207 -->

## Decision

Decision: `APPROVE_FAIL_CLOSEOUT`.

I approve task306/#369 as internally consistent corrected AIME2025 FAIL
closeout evidence for the task301 Qwen3-30B-A3B salvage checkpoint
`iter_0000035`. This is not a pass gate, not promotion clearance, not export or
endpoint clearance, not approval to merge #369 directly by worker_4, and not
authorization for further 30B or 8-GPU work.

The accepted comparison is:

- task306 FT checkpoint score: `14/30 = 0.4666666666666667`.
- accepted task300 30B base score: `15/30 = 0.5`.
- delta: `-1/30 = -0.033333333333333326`.
- task306 disposition: `FAIL`.

The global Qwen AIME 30B scale-up path should remain closed as
FAIL/no-promotion unless lead creates a new explicit follow-up task.

## Reviewed Inputs

- Lead docs head:
  `265646463c2bbac805a5765f14be508c1cc46fad`.
- Review PR: #369.
- Exact #369 head reviewed:
  `6ad9778ebed758cbcd72ee30ea71d9520a297ac7`.
- #369 state at review time: OPEN, base `main`, CLEAN/MERGEABLE, non-draft.
- task306 eval source head:
  `894e2e71e72f09926128e37f22000802804522bc`.
- Local artifact root:
  `/work-agents/intern_nemotron_worker_3/outputs/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_20260602T190432Z`.
- Remote artifact root:
  `/root/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_20260602T190432Z`.
- Worker_3 closeout mailboxes recorded in lead docs:
  `ae6fd1db7a894003a952469e4705ab07` and
  `094b16ec7ba14650b53bcd9e69306256`, plus the lead-observed session 6 PR
  follow-up.

## Commands And Checks

Static commands run:

- `gh pr view 369 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url`
- `git diff --name-status origin/main...6ad9778ebed758cbcd72ee30ea71d9520a297ac7`
- `git diff --name-status 894e2e71e72f09926128e37f22000802804522bc..1255f2356cb014cd1adbe58c7af297f291b222f3`
- `git diff --name-status 1255f2356cb014cd1adbe58c7af297f291b222f3..8201b3943db2d6ed4427c42518736c41f77d67bd`
- `git diff --name-status 8201b3943db2d6ed4427c42518736c41f77d67bd..6ad9778ebed758cbcd72ee30ea71d9520a297ac7`
- `git diff --stat` and targeted report diffs for the same drift ranges.
- Local `sha256sum` over the named key artifacts.
- Full local checksum-manifest replay from the artifact root:
  `cd <run_root>/artifacts && jq -r '.files[] | "\(.sha256)  \(.relative_path)"' manifests/checksum_manifest.json | sha256sum -c -`
- Python JSON inspection for summary/protocol/prompt/rank/load/boundary fields
  and JSONL row counts.
- Remote read-only key hash probe through `ssh NemTron`.

No training, eval rerun, canary run, base eval, export, endpoint launch,
promotion, task255 reuse, AIME2025 train-data use, shared deletion, product-code
edit, direct #369 approval, merge, or main push was performed.

## PR And Drift Scope

#369 at exact head `6ad9778ebed758cbcd72ee30ea71d9520a297ac7` contains only:

- `workspace/interns/intern_nemotron_worker_3/status.md`
- task306 README/history/task_knowledge/report files
- task306 no-export AIME runner file

No product code outside the task306 task directory is in scope.

Drift review:

- `894e2e71..1255f235`: worker_3 status plus task306 report/README/history/
  task_knowledge closeout for the completed run. This range introduces the
  retained task306 run report and runner docs.
- `1255f235..8201b394`: worker_3 status/session/PR metadata and task306
  README/history/task_knowledge/report metadata only. The report content changes
  PR/status wording, not the FAIL metrics or artifacts.
- `8201b394..6ad9778`: worker_3 queued-follow-up/status metadata only. The
  task306 report diff changes only the metadata session marker from session 5 to
  session 6; the FAIL metrics, artifact roots, hashes, and protocol evidence are
  unchanged.

`git diff --check` is clean for the PR diff and all three drift ranges.

## Artifact Verification

The local run root exists and the named key hashes match:

| Artifact | sha256 |
|---|---|
| `artifacts/aime_eval/summary.json` | `a3e046e3d5417095bd2d1072609dcdaf90ad17620015062efaac561e028ab947` |
| `artifacts/aime_eval/results.jsonl` | `46a702b31208661633b6b783e48f8fac3d6b60e06da3fdb9c3972a51cfa3f827` |
| `artifacts/aime_eval/full_completions.jsonl` | `32bb1e75f653711961b052a1008e53c668eb3787b8c5e3ea1369ed7ba8373704` |
| `artifacts/aime_eval/parser_diagnostics.jsonl` | `7c185fca5dc94105ff77aca48e70cfdeef8d5560a7b790682bdc312b2e807354` |
| `artifacts/manifests/checksum_manifest.json` | `a82f55bc0d9de7adb28aa28812a5d9b8d557a580ac6709cd7483452e3a8f02cd` |
| `artifacts/manifests/aime_prompt_manifest.json` | `23776fa86ca73f708f851b0355d0caaa00645267704ed309a7e5e4d2d94950f0` |
| `artifacts/manifests/checkpoint_load_manifest_rank0.json` | `fc5d745fb9df110b0c3bec639d87759fe4ebd13b9750d89e68f3d5d98ea4cf78` |
| `artifacts/manifests/command_env_manifest_rank0.json` | `0ea2edb381fe047d5280c3273dd0ef5a6faf525bac4e4870e5d1fc9dd9a86fdd` |
| `logs/remote_no_export_aime_eval.log` | `23f168f34636cd84946b5c4f8fee6a59c29670991e66ec2efcc5e9ef44c58fab` |
| `logs/remote_no_export_aime_eval_command.txt` | `e7ad13a6a14bcd6b81c91fa4dd994af5f39485700a7f58dc0c745a9143a8ada7` |
| `logs/remote_no_export_aime_eval.rc` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` |

The full local checksum manifest replay passed for all listed aggregate files,
rank files, rank event logs, prompt manifest, checkpoint-load manifests, and
command/env manifests.

Remote root key probe also matched the local key hashes for `summary.json`,
`results.jsonl`, `full_completions.jsonl`, `parser_diagnostics.jsonl`,
`checksum_manifest.json`, and `remote_no_export_aime_eval.rc`. The remote return
code file contains `0`.

Line-count and retention checks:

- `results.jsonl`: 30 rows.
- `full_completions.jsonl`: 30 rows.
- `parser_diagnostics.jsonl`: 30 rows.
- All rank `results_rank*.jsonl`, `full_completions_rank*.jsonl`, and
  `parser_diagnostics_rank*.jsonl`: 30 rows each.
- `full_text` non-empty rows in aggregate full completions: 30.
- `response_tail` non-empty rows in aggregate full completions: 30.

## Protocol Verification

Summary/protocol fields verified:

- `source_head`:
  `894e2e71e72f09926128e37f22000802804522bc`.
- Base model path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Candidate checkpoint:
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints/iter_0000035`.
- Route:
  `direct_in_process_mcore_static_engine_no_export_no_endpoint_30b_tp4_pp2_ep4_etp1_topk1_greedy_corrected_aime25`.
- Transport: `no_export_no_endpoint_mcore_static_engine`.
- Parallelism: world size 8, TP4, PP2, CP1, EP4, ETP1.
- Selected rank: rank 0 aggregate, with no best-correct rank selection.
- Requested rows: 30.
- Status `ok` rows: 30.
- Successful responses: 30.
- Correct rows: 14.
- Parsed rows: 17.
- Parsed rate: `0.5666666666666667`.
- Finish reasons: `stop=17`, `length=13`.
- Exact-normalized accuracy: `0.4666666666666667`.
- Accepted base comparison: base `15/30 = 0.5`, delta `-1`.

Checkpoint-load manifests for all 8 ranks report `load_megatron_model=PASS`,
model eval mode true, and the expected TP4/PP2/EP4 shape. Rank 0 event evidence
records effective parallelism overrides consistent with the summary.

Prompt/protocol continuity evidence:

- AIME prompt variant: `original`.
- Prompt manifest row count: 30.
- Prompt token mismatch count against task300 base artifacts: 0.
- AIME score cache sha:
  `c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74`.
- Same corrected AIME input cache, row count, all-request denominator, max
  tokens, parser, and normalizer are recorded against accepted task300 base
  evidence.
- Base artifact hashes recorded in task306 summary match accepted task300 base:
  summary `4a31904c118b09f80c1d77e7cd3aee0ede7117634b620092ea95e6306529e2ec`,
  results `19c853420a6827fa70b43db74bba987ba984a150e0e2c799234f0abfa26642fb`,
  full completions
  `27bf059b5a6a2868e75435af4b1c738e7ded5649a3d0b48cc52b4c7d76f243a7`,
  parser diagnostics
  `aefd30646c089ebfe5ae3c36ed0725a0ffb0217925ff711fb5790b7851d87d8e`,
  and checksum manifest
  `1fba8fea61e4ac179fea6c5e267f3cfb2005a3072f5b2e710287924c0c42abc0`.

## Sampling Residual

The task306 report correctly records `sampling_exact_parameter_match=false`.
Task300 base used SGLang `/v1/chat/completions` with `temperature=0` and
`top_p=1e-5`; task306 FT used the no-export MCore route with `top_k=1`,
`temperature=1`, and `top_p=0`.

This residual is acceptable for a FAIL closeout because the FT score is below
the accepted base score and the report does not claim a byte-identical endpoint
sampling proof. It would not be sufficient to support a pass, promotion, export,
or endpoint decision.

## Boundary Review

The command/env manifests record true boundary confirmations for:

- AIME2025 eval input only.
- No AIME2025 train prompts or labels.
- No task255 reuse.
- No training or optimizer steps in task306.
- Qwen3-30B only.
- No export or conversion.
- No endpoint or production endpoint.
- No promotion.
- No shared deletion.
- No main push or merge.

I found no artifact or diff evidence contradicting these confirmations.

## Runbook Closeout

Recommended lead closeout wording:

`APPROVE_FAIL_CLOSEOUT for task306/#369 exact head 6ad9778ebed758cbcd72ee30ea71d9520a297ac7 as corrected AIME2025 fail/no-promotion evidence only. The task301 Qwen3-30B-A3B iter_0000035 checkpoint scored 14/30 versus accepted 30B base 15/30 under the corrected 30-row AIME denominator. Artifacts, checksums, prompt/cache continuity, checkpoint-load manifests, and boundary records are internally consistent. Sampling exact-parameter mismatch remains a residual acceptable only for fail closeout. No promotion, export, endpoint, additional 30B training/eval, 30B/8-GPU work, or task255 reuse is authorized by this closeout.`

Residual risks:

- The base and FT routes are semantically greedy but not byte-identical in
  endpoint/transport/sampling parameters.
- The FT run has 13 length stops and 17 parsed rows, which is part of the
  observed failing result rather than a pass-quality artifact.
- This review did not rerun AIME, launch endpoints, train, export, or mutate
  worker_3 artifacts or branches.
