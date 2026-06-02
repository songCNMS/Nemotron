# task274 V11 Data Safety Readiness Review

<!-- METADATA:SESSION=1 -->

## Disposition

`BLOCK_PACKED_ARTIFACT_READY` for immediate Qwen3-4B pilot training from the
currently visible packed data.

`PASS_SOURCE_SAFETY` for the reviewed source/sidecar/decontamination evidence.

The data-side safety evidence is strong enough to define the next V11 data
inputs, but the old task253 packed split remains stale and is rejected by the
current task262 Qwen split guard. A future pilot must rematerialize/repack data
from the V11 blend plan under the merged task262 split logic before any
training can be considered.

## Reviewed Evidence

### task246 real heldout corpus

- Report:
  `workspace/tasks/task246_qwen_aime_v10_real_decontam_corpus_s1/real_decontam_corpus_report.md`
- Output root:
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1`
- Top manifest:
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/manifest.json`
- Top manifest sha256:
  `0a63ac5c1f019cc20dc2e8d4872f0f886d535defc860f28b13f712f36ba72313`
- Heldout corpus:
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl`
- Heldout corpus sha256:
  `614b2b347d33c1ec00cfd2c33222c26ad1d99b8b837bd7e48ea11fd4fedae6f9`
- Prompt hashes sha256:
  `a2a348ee12f962d5dd7ed7cf0e5d034ebea4a76a2287804e97ade331b552a78d`
- Reviewed counts: 560 rows, 560 unique prompt hashes, 0 label-like key leaks.
- M0 V10 sidecar input: 8 train rows, 0 val rows, 0 decontam-blocked V10
  candidates.

Status: acceptable as prompt-only heldout/decontamination corpus. AIME2025 is
held out for eval/decontamination only.

### task253 packed Qwen artifact

- Report:
  `/work-agents/intern_nemotron_worker_2/outputs/task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1/qwen_packing_xenna_unblock_report.md`
- Packed root:
  `/work-agents/intern_nemotron_worker_2/outputs/task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1/packed_qwen`
- Blend sha256:
  `963ad31c2265eaf9f10fdd261eb73705e72b83fbc0fff2b00f49891bfcbb0520`
- Metadata sha256:
  `18a83f43bdecaed886bd115945e3b767c99479bf6dafae20be544e21b36afac3`
- task253 original split summary: train 8 exposed shards / 79 rows / 596944
  input tokens / 110945 supervised tokens; valid 1 shard / 15 rows / 115993
  input tokens / 18998 supervised tokens.

Current V11 guard result:

```text
ValueError
Qwen packed split materialization mismatch for train: blend expects 15 parquet shard(s), exposed split has 8.
```

Status: stale and not acceptable as a future pilot packed training input. It is
useful only as historical evidence of the basename-collision failure.

### task254 independent packing review

- Remote branch:
  `origin/intern_nemotron_worker_5/task254_qwen_aime_v10_task253_packing_artifact_review_s1`
- Reviewed task253 head:
  `749ade2e05b18ae0f1083342eeef0f8a2d61b11e`
- Mailbox review:
  `685035aeac084a21a33edd0a1adf0bce`

Status: task254 approved task253 as local packing evidence only and preserved
global `NO-GO/HOLD`; it did not approve task253 as a candidate FT artifact.
That remains consistent with this review.

### task262 V11 split/sidecar repair

- PR #336 merged head:
  `8fd3ff6065290b850c98db5f7abff91aa6880967`
- Merge commit:
  `2ca6541c275d1eb64068e665af24147a796c818a`
- Output root:
  `/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1`
- Manifest sha256:
  `4c9874c9341b1e286533bd67eafa6a922567e905c9d3bb7bd78e8970eb777383`
- Split audit sha256:
  `b2009b2c509620c5dde2412ee4dedf4efb8995431ef4bec4d353ba14dc3787b3`
- V11 blend plan sha256:
  `2b3f0942eb04e077c5025c60be87355bf233b33085660a0b85a0b8b03b569e2a`
- Final-answer n-gram scan sha256:
  `feffa6c677b1bc86b5f2f9ad8a8c3506582844cdb5b6a25bd8741322a9298370`

task262 split audit:

| Split | Intended shards | Exposed shards | Intended rows | Exposed rows | Intended input tokens | Exposed input tokens | Intended supervised tokens | Exposed supervised tokens | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| train | 15 | 8 | 113 | 79 | 835223 | 596944 | 156569 | 110945 | MISMATCH |
| valid | 1 | 1 | 15 | 15 | 115993 | 115993 | 18998 | 18998 | MATCH |

V11 source/sidecar plan:

| Source | Rows | Weight | SHA256 |
|---|---:|---:|---|
| base M0 train | 1100 | 1.0 | `994166eeb83ffb5ebd213db9cc0d6cdd90208251bd2aab9dbb70cec7bf96691a` |
| hard-math full solution | 8 | 1.0 | `2039b67b2bcf5cf74b576a640f1f3a198d675e3fbd64a886da4be5753ad515d9` |
| final-answer | 200 | 1.0 | `0e5485eae86bf716d0c2e04e8e02595564b38a949d71d31a42874d6e87ef1731` |

Final-answer full scan:

| Final-answer rows | Heldout prompts | Pair comparisons | Overlap pairs | Informational pairs | Blocker pairs | Rows with blocker overlap | Max score |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 200 | 560 | 112000 | 4 | 1 | 0 | 0 | 0.257143 |

Standard `decontaminate_math_rows` with token 8-grams, blocker threshold 0.5,
and target environment `math_competition_numeric` scanned 100 final-answer
rows, found 0 blocker findings, and dropped 0 rows.

Status: acceptable as V11 data/split repair evidence and as the source plan for
a future rematerialization. It is not itself a materialized packed training
artifact.

### task265 independent review

task265 evidence is recorded in PR #336 gate comments. The lead approval
comment for exact head `8fd3ff6065290b850c98db5f7abff91aa6880967` states that
worker_4/task265 independently verified:

- `git diff --check` PASS;
- `py_compile` PASS;
- focused pytest 26/26 PASS;
- artifact checksum verification PASS;
- final-answer n-gram scan with 112000 pair comparisons, 0 blocker pairs at
  threshold >= 0.5, and 0 exact prompt-hash overlaps;
- no AIME25 train leakage found.

Status: task265 clears the task262 data-safety concern after the final-answer
scan evidence, but approval remains scoped to data split/sidecar repair
evidence only.

## Current Decontamination Rules

Read-only inspection of
`src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py`
confirmed:

- default n-gram size: 8;
- blocker threshold: 0.5;
- math decontam target environment: `math_competition_numeric`.

V10-style hard-math strategies still require a decontamination corpus and do
not waive heldout AIME2025 rules.

## Checks Run

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
```

```bash
PYTHONPATH=src python - <<'PY'
# Loaded task246/task253/task262 manifests and JSONL/JSON artifacts.
# Verified sha256 values, heldout row/hash counts, label-like heldout keys,
# task262 split audit counts, V11 blend plan rows/weights, final-answer scan
# counts, exact heldout prompt-hash overlap counts, and decontam constants.
PY
```

```bash
PYTHONPATH=src python - <<'PY'
from pathlib import Path
from nemotron.recipes.super3.stage1_sft.qwen_chat_contract import validate_qwen_packed_sft_chat_contract
validate_qwen_packed_sft_chat_contract(
    Path('/work-agents/intern_nemotron_worker_2/outputs/task253_qwen_aime_v10_qwen_packing_xenna_unblock_s1/packed_qwen/splits'),
    tokenizer_model='/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507',
)
PY
```

The current Qwen packed-data guard failed as expected on the stale task253
artifact with `blend expects 15 parquet shard(s), exposed split has 8`.

```bash
gh pr view 336 --comments --json comments,reviews,number,url,state,headRefOid,mergeCommit,mergedAt
```

Used to confirm the task265 independent review and final lead approval record.

```bash
git diff --check
```

## Artifact Disposition

| Artifact | Status | Rationale |
|---|---|---|
| task246 heldout corpus and prompt hashes | ACCEPTABLE | Prompt-only heldout, 560 rows/hash count, no label-like keys. |
| task246 M0 V10 sidecar input | ACCEPTABLE BUT SPARSE | 8 train rows, 0 val rows, 0 decontam drops; low row count remains a pilot limitation. |
| task251 base/hard/final-answer JSONLs referenced by task262 | ACCEPTABLE AS SOURCE INPUTS | Exact heldout prompt-hash overlaps are 0; final-answer full scan has 0 blocker rows. |
| task253 `packed_qwen/splits` | STALE / DO NOT USE FOR TRAINING | Current task262 Qwen contract rejects train split: 15 intended shards versus 8 exposed. |
| task262 V11 blend plan | ACCEPTABLE AS REMATERIALIZATION PLAN | Includes base 1100, hard 8, final-answer 200 with explicit weights and clean decontam evidence. |
| task262 final-answer scan | ACCEPTABLE | 200 x 560 full token 8-gram scan, 0 blocker pairs/rows. |

## Exact Data Readiness Blocker

The exact blocker before any future Qwen3-4B V11 pilot training is:

`No current accepted collision-safe rematerialized packed_qwen artifact exists.`

A future implementation task must run data prep from the task262 V11 blend plan
under the merged task262 split materialization logic, then verify:

- `splits/manifest.json` exists;
- intended and exposed train/valid targets match as multisets;
- train/valid row, token, supervised-token, shard, and source counts are
  recorded;
- Qwen packed-data contract passes;
- no AIME2025 prompts or labels are in trainable outputs;
- task246 heldout corpus remains used only for eval/decontamination.

## Boundary Confirmation

This review did not create or modify training data, run training, run live
AIME/task243 eval, export, launch endpoints, promote, use AIME2025 train data,
use 30B/8-GPU, merge, push main, or delete/overwrite shared files.
