# task334 independent review of task333/#396

<!-- METADATA:STATUS=ReadyForPR,DISPOSITION=REQUEST_CHANGES_REPORT_ARTIFACT_MISMATCH,SESSION=1 -->

Generated: 2026-06-04T08:07:02Z

## Decision

`REQUEST_CHANGES_REPORT_ARTIFACT_MISMATCH` for #396 exact head
`8546ae8dc25c9f6a5bf06fdf48d8766677b8b75e`.

Most reviewed artifact checks passed for the assigned task333 run root
`/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z`.
However, the committed #396 report names that `run_20260604T074500Z` root while
its Source Provenance table carries three task299 row-manifest hashes from a
different, unassigned `run_20260604T083000Z` root. Because task334 explicitly
requires report consistency with `run_20260604T074500Z`, I do not recommend
approving #396 until the report/head is refreshed or lead explicitly retargets
the review to the later run.

This review does not authorize task310 release, training, optimizer steps,
nonzero-LR smoke, benchmark eval, export, endpoint, promotion, 30B release,
task255 reuse, AIME2025 train rows, shared deletion, main push, merge, or
self-merge.

## Target Reviewed

- PR: #396 `https://github.com/songCNMS/Nemotron/pull/396`
- PR state observed: `OPEN`, non-draft, base `main`, `CLEAN`/`MERGEABLE`
- Exact head reviewed: `8546ae8dc25c9f6a5bf06fdf48d8766677b8b75e`
- Base observed: `origin/main` `ad0c5a7d758d44370695b94c83385591f100c714`
- Artifact root reviewed:
  `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z`
- Packed root reviewed:
  `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z/packed_qwen_combined_contract`

## Checks Run

Commands were run from
`/work-agents/intern_nemotron_worker_4/Nemotron_task334` unless noted.

```bash
git fetch origin main +pull/396/head:refs/remotes/origin/pr/396
gh pr view 396 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
git diff --name-status origin/main...origin/pr/396
git diff --check origin/main...origin/pr/396
python3 - <<'PY'
import subprocess
path='workspace/tasks/task333_qwen_all_sft_combined_packed_contract_s1/build_task333_combined_packed_contract.py'
src=subprocess.check_output(['git','show','origin/pr/396:'+path])
compile(src, path, 'exec')
print('helper_compile=PASS')
PY
cd /work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z
sha256sum -c manifests/artifact_checksums.sha256
sha256sum -c manifests/packed_shard_checksums.sha256
cat logs/qwen30b_contract_validate.rc
tail -n 20 logs/qwen30b_contract_validate.log
sha256sum row_manifests/*.rows.tsv.gz
python3 <read-only manifest/report consistency and symlink summary script>
```

Results:

- #396 head remained exact `8546ae8dc25c9f6a5bf06fdf48d8766677b8b75e`.
- Diff scope was limited to worker_1 status plus task333 docs/report/helper:
  `workspace/interns/intern_nemotron_worker_1/status.md` and
  `workspace/tasks/task333_qwen_all_sft_combined_packed_contract_s1/*`.
- `git diff --check origin/main...origin/pr/396`: clean.
- Helper compile from the PR head: `PASS`.
- `sha256sum -c manifests/artifact_checksums.sha256`: all 15 entries `OK`.
- `sha256sum -c manifests/packed_shard_checksums.sha256`: all 96 packed shard
  entries `OK`.
- Qwen30B contract validation rc: `0`; log marker:
  `TASK333_QWEN30B_PACKED_CONTRACT=PASS`.
- Split symlink check: 96 symlinks, 0 broken; train 84, valid 6, test 6.

## Passing Evidence

The assigned `run_20260604T074500Z` artifact manifests support the main packed
contract claims:

- Manifest disposition:
  `PASS_COMBINED_PACKED_CONTRACT_READY_FOR_REVIEW`.
- Total packed metrics: 96 shards, 89,325 rows, 342,875,996 input tokens,
  38,245,535 supervised tokens, 175,969,867 bytes.
- Split metrics:
  - train: 84 shards, 78,168 rows, 300,046,415 input tokens,
    33,477,337 supervised tokens.
  - valid: 6 shards, 5,561 rows, 21,365,088 input tokens,
    2,373,422 supervised tokens.
  - test: 6 shards, 5,596 rows, 21,464,493 input tokens,
    2,394,776 supervised tokens.
- Source metrics:
  - `agentic-interactive`: 35,323 rows, 122,527,221 input tokens,
    7,568,103 supervised tokens.
  - `instruction-following-structured`: 2,693 rows, 10,307,854 input tokens,
    1,922,762 supervised tokens.
  - `m1-agentic-sft-v11-from-m0`: 244 rows, 942,062 input tokens,
    167,555 supervised tokens.
  - `m1-agentic-sft-v11-math-final-answer`: 28 rows, 75,305 input tokens,
    54,821 supervised tokens.
  - `m1-agentic-sft-v11-math-hard-verified-full-solution`: 8 rows,
    8,770 input tokens, 7,979 supervised tokens.
  - `swe`: 51,029 rows, 209,014,784 input tokens,
    28,524,315 supervised tokens.
- Intended-vs-exposed multiset parity: pass for train, valid, and test.
- Qwen packed/training contract: rc 0, PASS marker present.
- Decontam/no-forbidden-source proof:
  - `aime2025_prompt_or_label_train_rows`: 0.
  - `task255_reuse`: not used.
  - all nine task327 `BLOCKED_DECONTAM_HIT` sources excluded.
  - task329 zero-supervised SWE excluded and replaced with task331
    no-tools-header SWE.
  - six task332 structured validation-filtered rows excluded fail-closed.
- Task332 split policy is represented: source-local shard 14 valid, shard 15
  test, all other shards train.

## Request-Changes Finding

The committed #396 report is inconsistent with the assigned artifact root for
three task299 row-manifest hashes.

| Source | #396 report row manifest sha256 | `074500Z` manifest/file sha256 |
|---|---|---|
| `m1-agentic-sft-v11-from-m0` | `5894818a7fcfea644e202da10f551f3de844b8369432221c376e5121ef80cd15` | `7562c86407e00c890ba86eb150a28c8c9bfbc1d7d35eb2c43bfbc5a9af878599` |
| `m1-agentic-sft-v11-math-final-answer` | `ca07a194e74131b726252bd2589a83c0572ef9bb04c426b710032fcbdc1bb521` | `e466ee7bd8032ff45596073d21c75f482611689edee3a20a9f5ade440a1ac653` |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | `f1373026c688817a7e47f6060878f975e9bf125e959aee6375bcf49149cf4820` | `89ab29ebe1ab5a11e4467652ff40a855612e1ef4a47d024bbdc02eb9cd965e2f` |

`run_20260604T074500Z/manifest.json`,
`run_20260604T074500Z/manifests/source_provenance.json`, and direct
`sha256sum row_manifests/*.rows.tsv.gz` agree on the `074500Z` values. The
hashes printed in the #396 report were found in a separate local
`run_20260604T083000Z` artifact root, which is not the assigned task334 review
root and is not the root named in the #396 report.

This appears to be a report/provenance transcription or stale-artifact issue,
not evidence that the `074500Z` packed root itself failed checksum or contract
validation. It still prevents approval of the current #396 head as written.

## Residual Risks

- No fresh task333 decontam scan was run; task333 carries accepted upstream
  decontam proofs.
- The task299 seed still lacks a normalized-prompt hit field; this is carried
  as a residual rather than newly asserted.
- The hard-math task299 source exposes valid/test shard files with zero rows.
- SWE rows still truncate to 4096 tokens, inherited from task331, but have
  nonzero supervised tokens in the Qwen pack window.
- The combined root is a symlink/materialization contract over accepted
  upstream packed shards, not a task310 release or training pass.

## Required Fix Before Approval

Worker_1 should refresh #396 so the committed task333 report and any referenced
manifest/checksum evidence consistently target the same artifact root. Either:

- correct the report for `run_20260604T074500Z` using the `074500Z` row-manifest
  hashes above, or
- if lead wants the later `run_20260604T083000Z` artifacts reviewed, update the
  PR/report/lead assignment to that exact root and request a new exact-head
  review.
