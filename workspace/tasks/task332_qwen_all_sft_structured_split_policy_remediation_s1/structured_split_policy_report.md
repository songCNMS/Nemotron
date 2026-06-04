# task332 structured split policy remediation report

## Disposition

Decision: `PASS_SPLIT_POLICY_READY_WITH_SWE_PENDING`.

I produced task-owned, no-training remediation evidence for the two non-SWE
task329 blockers: the 6 `instruction-following-structured` validation-filtered
rows and the sparse valid/test split exposure. The structured rows are exactly
identified and must remain fail-closed/excluded unless a later source fix adds
the missing tool context and re-runs the same validator. A deterministic
per-source split policy is ready for a later combined packed-contract task.

This does not release task310, training, benchmark eval, export, endpoint, or
promotion. SWE remains blocked until task331 proves nonzero supervised tokens.

## Snapshot

| Item | Value |
| --- | --- |
| Worker branch | `intern_nemotron_worker_4/task332_qwen_all_sft_structured_split_policy_remediation_s1` |
| Worker PR | #394 `https://github.com/songCNMS/Nemotron/pull/394` |
| Base | `origin/main` `410c2247fc5e09e6ad831bdee1628830b97fbd89` |
| Task docs imported | `bbbf19df7ea7dad3fc644588f1e84240c464febe` |
| Task329 root | `/work-agents/intern_nemotron_worker_2/outputs/task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z` |
| Task332 output root | `/work-agents/intern_nemotron_worker_4/outputs/task332_qwen_all_sft_structured_split_policy_remediation_s1/run_20260604T065013Z` |
| Task331 dependency branch | `origin/intern_nemotron_worker_2/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1` |
| Task331 visible head | `63b4b992d534bd16120f31345d57d105890d8d55` |
| Task331 PR search | `[]` |

## Structured Row Evidence

Validator used:
`nemotron.data_prep.core.chat_template.validate_conversation`.

The validator rejects rows with `<tool_call>` present in message content or
reasoning content when no message includes `# Tools`. The six identified rows
all have `<tool_call>` occurrences and zero `# Tools` occurrences.

| Row index | UUID | Shard | Row SHA256 | Tool calls | `# Tools` |
| ---: | --- | ---: | --- | ---: | ---: |
| 3714 | `4b560c38-27b6-40f4-af41-f2c70df252a9` | 2 | `93b2f43d8d7d06506385124acf2bb5a8afc2063735638a0d7dbe2cba66e6e1a0` | 1 | 0 |
| 276 | `79468959-929d-4daf-a5ff-d2e43f2f7644` | 4 | `6c70aaad66b17d2516495bc78a10c4bb72ba804dd21af2b0e48a2d8d37d0b409` | 3 | 0 |
| 1702 | `592cb371-797b-4a7f-b48e-f07c2b0a4e5a` | 6 | `2794715a6ffb2a7dfc73e7a68d3b4b53ec591d2015b36c0d6d41bbc99951898e` | 1 | 0 |
| 2888 | `ab7a0cfe-faf3-4a54-9b91-bf40d78e406d` | 8 | `b8c5e83a7fef550ecca02d238a76be4b12dfa734c6511620f1cf979f3817d4c1` | 1 | 0 |
| 1579 | `a60f1e9c-40c0-43c4-a2be-52fd4cc1b559` | 11 | `89e61287665c4bc4341f43b82e24dd8001ee75418f38e823ffdc680c7ecac1d7` | 1 | 0 |
| 1566 | `001e690e-e784-465f-9404-98c1cc0762c4` | 14 | `5279fedefe55312a084683b1a580733e6eceabcfb342411a3e1c9aca6a306eb9` | 1 | 0 |

Receipt match: `true`.

Task329 structured receipts report 4,969 input rows, 4,963 output sequences,
2,693 packed rows, 6 filtered rows, and 6 validation errors. The six row
indices above land one each in shards `000002`, `000004`, `000006`, `000008`,
`000011`, and `000014`, matching task329 receipt validation-error shards.

Disposition: exclude these exact row hashes/indices fail-closed from SFT unless
a later source-remediation task repairs the missing tool schema/header context
and re-runs the same validator.

## Split Policy

Policy id: `task332_per_source_shard_holdout_v1`.

Rule: for every included raw-pass source, shard rows by `row_index % 16`;
assign remainder `14` to valid, remainder `15` to test, and all other
remainders to train.

This is deterministic, source-local, and guarantees train/valid/test exposure
for each included source. It is not applied to the existing task329 split
artifact; it is intended for the later combined-contract/materialization task.

Projected metrics if relinked from task329 per-source shards after structured
row exclusion:

| Split | Shards | Packed rows | Input tokens | Supervised tokens | Raw eligible rows | Validation-excluded rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 42 | 77,921 | 299,145,687 | 8,299,021 | 65,645 | 5 |
| valid | 3 | 5,544 | 21,302,331 | 592,468 | 4,687 | 1 |
| test | 3 | 5,580 | 21,401,841 | 599,376 | 4,688 | 0 |

Per-source exposure under the policy:

| Source | Train | Valid | Test | Residual |
| --- | --- | --- | --- | --- |
| `agentic-interactive` | yes | yes | yes | none for split exposure |
| `instruction-following-structured` | yes | yes | yes | six rows excluded fail-closed |
| `swe` | yes | yes | yes | current task329 supervised_tokens remain `0`; task331 required |

The current task329 split remains sparse: valid/test expose only
`agentic-interactive`; `instruction-following-structured` and `swe` are train
only. Task332 does not accept that sparse exposure as a combined training
contract; it provides a deterministic replacement policy.

## Decontam And Source Checks

Raw source checksums and counts:

| Source | Rows | SHA256 |
| --- | ---: | --- |
| `agentic-interactive` | 19,028 | `dcfeda22372fa707c979cab29ddfe896b89a933f15ed4acbb4f16e7e3787d9dd` |
| `instruction-following-structured` | 4,969 | `03e4cc9a657f9f193860d82fe49764acc6b298f6ce6811497412aa5a0181ec77` |
| `swe` | 51,029 | `1e0fb6d9a8d955fb0f2160e44a4946e5f2c4eb3931e80dadb724ff823cdbc14c` |

The carried decontam manifest status is
`PASS_NO_AIME2025_TRAIN_ROWS_BY_PRIOR_DECONTAM_AND_SOURCE_EXCLUSION`.
All included sources have zero prompt-hash, normalized-prompt, and n-gram
hits. All nine task327 decontam-hit sources remain excluded:
`agentic-tool-calling`, `competitive-cpp-00`, `competitive-cpp-01`,
`competitive-python-00`, `competitive-python-01`, `infinibyte-00`,
`infinibyte-01`, `instruction-following-chat`, and `math-proofs-lean`.

## Task331 Dependency

Task331 is still pending. The visible branch head is
`63b4b992d534bd16120f31345d57d105890d8d55`, with no PR visible from
`gh pr list --search task331...`. Its diff versus `origin/main` is
acceptance/status/docs only:

- `workspace/interns/intern_nemotron_worker_2/status.md`
- `workspace/tasks/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/README.md`
- `workspace/tasks/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/history_log.md`
- `workspace/tasks/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/task_knowledge.md`

Required next condition: task331 must produce lead-reviewed SWE formatter/config
evidence with nonzero Qwen supervised tokens before any combined all-SFT packed
contract or task310 release.

## Artifacts

Task332 output root:
`/work-agents/intern_nemotron_worker_4/outputs/task332_qwen_all_sft_structured_split_policy_remediation_s1/run_20260604T065013Z`

Key manifests:

- `manifests/structured_filtered_rows.jsonl`
- `manifests/structured_filtered_rows_summary.json`
- `manifests/split_policy.json`
- `manifests/proposed_intended_vs_exposed_manifest.json`
- `manifests/decontam_no_aime2025_train_proof.json`
- `manifests/task331_dependency.json`
- `manifests/raw_source_checksums_and_counts.json`
- `manifests/command_env_manifest.json`
- `manifests/final_summary.json`
- `manifests/artifact_checksums.sha256`

Checksum file SHA256:
`85dc9e1bc120cdb5c7b3ab8edeea541b4ab95ad6ef97195d9e35c95c3ebfaee3`.

`sha256sum -c manifests/artifact_checksums.sha256` passed for all generated
manifest entries.

## Commands

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git rev-parse HEAD
git rev-parse origin/main
git rev-parse origin/intern_nemotron_worker_2/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1
git diff --name-status origin/main...origin/intern_nemotron_worker_2/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1
gh pr list --state all --search "task331_qwen_all_sft_swe_supervised_formatter_unblock_s1" --json number,state,headRefName,headRefOid,title,url
PYTHONPATH=src python workspace/tasks/task332_qwen_all_sft_structured_split_policy_remediation_s1/build_task332_structured_split_policy_evidence.py --run-id run_20260604T065013Z
python -m py_compile workspace/tasks/task332_qwen_all_sft_structured_split_policy_remediation_s1/build_task332_structured_split_policy_evidence.py
sha256sum -c manifests/artifact_checksums.sha256
```

## Boundaries

I did not train, run optimizer steps, pack a new training artifact, run eval,
export, launch an endpoint, promote, reuse task255, use AIME2025 prompt/label
train rows, delete shared files, mutate task329 artifacts, merge, self-merge,
or push main. Changes are scoped to task332 docs/status and a task-local helper.
