# task299 30B data/packing contract report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_1,SESSION=83 -->

## Decision

Decision: `PASS_30B_DATA_PACKING_CONTRACT`.

Task276 V11 packed data is safe to adapt for
`Qwen3-30B-A3B-Instruct-2507` because the Qwen3-4B and Qwen3-30B-A3B tokenizer
assets, tokenizer-native chat-template rendering, split materialization,
offline packed/training contract validators, and decontamination evidence all
passed. The task-owned 30B-ready packed root is:

`/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`

This is data/packing contract evidence only. It does not authorize training,
testing, AIME/task243 eval, canary, export, endpoint, promotion, task255 reuse,
shared deletion, main push, merge, 30B training, or 8-GPU launch.

## Commands And Environment

Repository:
`/work-agents/intern_nemotron_worker_1/Nemotron`

Current main:
`31137bc1e28f7d08d4c6b5aa2448487d95aa07d7`

Lead docs branch:
`676d85563e00dfb665b6a911995bd47b4932c370`

Commands used:

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git rev-parse origin/main
git rev-parse origin/intern_nemotron_lead/session1-recovery-task-docs
git checkout origin/intern_nemotron_lead/session1-recovery-task-docs -- workspace/tasks/task299_qwen_aime_v11_30b_data_packing_contract_s1
python3 - <<'PY'
# tokenizer-native AutoTokenizer probe for Qwen3-4B and Qwen3-30B-A3B
PY
sha256sum <4B and 30B tokenizer assets>
PYTHONPATH=src python3 - <<'PY'
# task-owned artifact generator:
# - copy task276 packed root to worker_1 outputs
# - rewrite split symlinks/blend/manifest to copied root
# - update metadata tokenizer_uri to Qwen3-30B-A3B after equivalence proof
# - run validate_qwen_packed_sft_chat_contract
# - run validate_qwen_training_pipeline_contract with qwen profile and 30B tokenizer
# - compute split counts/parity, shard checksums, and decontam proof
PY
jq <manifest/contract/tokenizer/decontam probes>
find <packed splits> -type l -xtype l -print | wc -l
git diff --check
```

No training, testing, optimizer step, AIME scoring/eval, canary, export,
endpoint, promotion, task255 reuse, shared deletion, main push, merge, 30B
training, or 8-GPU launch was run.

## Artifacts

Run root:
`/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z`

Top manifest:
`/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/manifest.json`

Top manifest sha256:
`59ee4432b5ddf776f82ee5dff6f45f1a9c1f8f9c7ad99a29d8fcfb96c7e50f3d`

Artifact checksums:

| Artifact | sha256 |
|---|---|
| `tokenizer_chat_template_equivalence_probe.json` | `f31d5229da06ef1ff7c5457acfd66a7b4b4c91e92c61d7ae00f4492b476000ec` |
| `contract_validation.json` | `75265f68621676c846551ba12022cb3d6f383b4f65e3bc7fb9773a197434d0b2` |
| `split_counts_parity.json` | `f4c335e651cc7777ecf326ed2fa3e46791c3de7286d7dee86042d941db2be70d` |
| `decontam_proof.json` | `e5b73a79ae8d1cd35b3188bd0f6bda60570f37c21831ac16d126a006d7fd56bc` |
| `packed_qwen_30b_shard_checksums.json` | `444aef9230129d689c27be295ff054fc1dc4800fae52827280a5c289408fed11` |
| `packed_qwen_30b_shard_checksums.sha256` | `ff592c935f09037d81a2aceb9dc394189c871623cebf1a1d92dd9b4233d493fa` |
| `packed_qwen_30b/splits/metadata.json` | `e6aedb275e3505521ef5878647883bfb46aa8462830fdd742cefa3d59a6c0733` |
| `packed_qwen_30b/splits/manifest.json` | `3fd3fa7314d1e397bbff98cc9f5cb77e9973925e6d5914e410f14c42dc2f091b` |
| `packed_qwen_30b/blend.json` | `e19f2b8a54714c97e88d380a7be8b278794be1ee57ff60abff6047a88217940a` |

Shard checksum list contains `48` copied parquet shard files.

The final packed metadata records:

- tokenizer URI:
  `file:///mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- blend path:
  `/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b/blend.json`
- `chat_template`: `tokenizer`
- `chat_template_kwargs.enable_thinking`: `false`
- `chat_template_kwargs.truncate_history_thinking`: `false`
- copied packed token IDs unchanged from task276.

Split symlink sanity check found `0` broken symlinks.

## Tokenizer And Chat Template

Compared:

- 4B: `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
- 30B: `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`

Tokenizer asset hashes match:

| File | sha256 |
|---|---|
| `tokenizer.json` | `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4` |
| `tokenizer_config.json` | `a62ff0a2472a0fa1b8eaabcb57c59b58afa42a22831dc141400b6e0cf2b65ce3` |
| `vocab.json` | `ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910` |
| `merges.txt` | `599bab54075088774b1733fde865d5bd747cbcc7a547c5bc12610e874e26f5e3` |

Tokenizer-native API proof:

- class: `Qwen2TokenizerFast` for both
- vocab size: `151643` for both
- tokenizer length: `151669` for both
- EOS token id: `151645` for both
- PAD token id: `151643` for both
- BOS token id: `null` for both
- chat-template sha256:
  `64f85b198065d0fba2a81f37e10ed68161ce2c19a754c7100e67e0ca2ee9c326`
  for both
- special token map equal: `true`

Tokenizer-native `apply_chat_template` samples from all three task276 source
datasets rendered identical text and identical token IDs:

| Source | Token count | rendered/token ids equal |
|---|---:|---|
| `m1-agentic-sft-v11-from-m0` | `222` | yes |
| `m1-agentic-sft-v11-math-final-answer` | `275` | yes |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | `1270` | yes |

## Contract Validators

Offline, no-training validators:

- `validate_qwen_packed_sft_chat_contract`: `PASS`
- `validate_qwen_training_pipeline_contract`: `PASS`

Both validators used the task-owned 30B packed root and target tokenizer
`/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.

## Split Counts And Parity

Intended-vs-exposed multiset parity passed for all splits.

| Split | Exposed shards | Rows | Input tokens | Supervised tokens | Parity |
|---|---:|---:|---:|---:|---|
| train | 46 | 279 | 1,024,646 | 228,927 | PASS |
| valid | 1 | 1 | 1,491 | 1,428 | PASS |
| test | 1 | 0 | 0 | 0 | PASS |

Train source counts:

| Source | Shards | Rows | Input tokens | Supervised tokens |
|---|---:|---:|---:|---:|
| `m1-agentic-sft-v11-from-m0` | 16 | 244 | 942,062 | 167,555 |
| `m1-agentic-sft-v11-math-final-answer` | 16 | 28 | 75,305 | 54,821 |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | 14 | 7 | 7,279 | 6,551 |

Valid and test each expose one hard-math shard. Valid contains one packed row;
test contains zero rows, matching task276 semantics.

## Decontamination

Decision: `PASS`.

Heldout evidence:

- task246 heldout prompt hashes: `560`
- heldout prompt hash list sha256:
  `a2a348ee12f962d5dd7ed7cf0e5d034ebea4a76a2287804e97ade331b552a78d`
- heldout corpus sha256:
  `614b2b347d33c1ec00cfd2c33222c26ad1d99b8b837bd7e48ea11fd4fedae6f9`

Current task299 source scan:

| Source | Rows scanned | AIME contest mentions | Label-like top-level keys | task246 user prompt hash overlap | task246 system+user hash overlap |
|---|---:|---:|---:|---:|---:|
| `m1-agentic-sft-v11-from-m0` | 1100 | 0 | 0 | 0 | 0 |
| `m1-agentic-sft-v11-math-final-answer` | 200 | 0 | 0 | 0 | 0 |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | 8 | 0 | 0 | 0 | 0 |

Task262 final-answer n-gram decontam scan carried forward:

- scan sha256:
  `feffa6c677b1bc86b5f2f9ad8a8c3506582844cdb5b6a25bd8741322a9298370`
- blocked rows: `0`
- blocker pairs: `0`
- exact prompt hash overlap: `0`
- final-answer rows scanned: `200`
- heldout rows scanned: `560`
- n-gram size: `8`

AIME2025 prompts/labels remain held out for eval/decontam only and are not
trainable rows.

## Residuals

- This is an adapted metadata/root copy, not a fresh 30B re-tokenization run.
  That is acceptable because tokenizer assets, chat template, native rendering,
  and token IDs are proven identical for Qwen3-4B-Instruct-2507 and
  Qwen3-30B-A3B-Instruct-2507.
- Validation/test split sparsity is inherited from task276: valid has one packed
  row and test has zero rows.
- A partial earlier worker-owned artifact attempt under
  `run_20260602T150732Z` failed before validation due to a path-rewrite bug and
  is not the accepted artifact root. The accepted root is `run_20260602T150941Z`.

## Boundary Confirmation

No training, testing, optimizer step, corrected AIME scoring/eval, non-AIME
canary, export, endpoint, promotion, task255 reuse, AIME2025 train prompts or
labels, shared deletion, main push, merge, 30B training, or 8-GPU launch was
performed.
