# task334 independent review of task333/#396

<!-- METADATA:STATUS=ReadyForPR,DISPOSITION=APPROVE_COMBINED_PACKED_CONTRACT_FOR_DOCS_CLOSEOUT,SESSION=2 -->

Generated: 2026-06-04T08:24:34Z

## Decision

`APPROVE_COMBINED_PACKED_CONTRACT_FOR_DOCS_CLOSEOUT` for #396 exact head
`6261daaa37172caa11929b0b88f685b63f987221`.

The prior task334 review found a report/artifact mismatch at #396 head
`8546ae8dc25c9f6a5bf06fdf48d8766677b8b75e`: the report named the assigned
`run_20260604T074500Z` root but contained three task299 row-manifest hashes
from a separate local `run_20260604T083000Z` root. Worker_1 refreshed #396 first
to head `9a9471e35e3d80f6bf2995478ddf4bd1ef785a66`, then advanced to current
head `6261daaa37172caa11929b0b88f685b63f987221`. My independent refresh
verified that `8546ae8d..9a9471e3` is worker_1 status plus task333 report hash
correction, `9a9471e3..6261daaa` is non-material worker_1
status/history/task_knowledge bookkeeping only, and the corrected #396 report
at `6261daaa` matches the assigned `run_20260604T074500Z` artifacts.

This approval is docs/evidence closeout only. It does not authorize task310
release, training, optimizer steps, nonzero-LR smoke, benchmark eval, export,
endpoint, promotion, 30B release, task255 reuse, AIME2025 train rows, shared
deletion, main push, merge, or self-merge.

## Target Reviewed

- PR: #396 `https://github.com/songCNMS/Nemotron/pull/396`
- PR state observed: `OPEN`, non-draft, base `main`, `CLEAN`/`MERGEABLE`
- Exact head reviewed: `6261daaa37172caa11929b0b88f685b63f987221`
- Previous reviewed heads:
  `8546ae8dc25c9f6a5bf06fdf48d8766677b8b75e`,
  `9a9471e35e3d80f6bf2995478ddf4bd1ef785a66`
- Base observed: `origin/main` `ad0c5a7d758d44370695b94c83385591f100c714`
- Artifact root reviewed:
  `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z`
- Packed root reviewed:
  `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z/packed_qwen_combined_contract`

## Commands And Checks

Commands were run from
`/work-agents/intern_nemotron_worker_4/Nemotron_task334` unless noted.

```bash
git fetch origin main +pull/396/head:refs/remotes/origin/pr/396 +pull/397/head:refs/remotes/origin/pr/397
gh pr view 396 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
gh pr view 397 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
git diff --name-status 8546ae8dc25c9f6a5bf06fdf48d8766677b8b75e..9a9471e35e3d80f6bf2995478ddf4bd1ef785a66
git diff --check 8546ae8dc25c9f6a5bf06fdf48d8766677b8b75e..9a9471e35e3d80f6bf2995478ddf4bd1ef785a66
git diff --name-status 9a9471e35e3d80f6bf2995478ddf4bd1ef785a66..6261daaa37172caa11929b0b88f685b63f987221
git diff --check 9a9471e35e3d80f6bf2995478ddf4bd1ef785a66..6261daaa37172caa11929b0b88f685b63f987221
git diff --name-status origin/main...origin/pr/396
git diff --check origin/main...origin/pr/396
python3 <helper compile from origin/pr/396>
python3 <report/source_provenance/direct sha256 consistency check>
cd /work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z
sha256sum -c manifests/artifact_checksums.sha256
sha256sum -c manifests/packed_shard_checksums.sha256
cat logs/qwen30b_contract_validate.rc
tail -n 5 logs/qwen30b_contract_validate.log
python3 <split symlink and intended-vs-exposed parity summary>
```

Results:

- #396 current head is exact
  `6261daaa37172caa11929b0b88f685b63f987221`, `OPEN`, non-draft, base
  `main`, `CLEAN`/`MERGEABLE`.
- #397 current head before this refresh was exact
  `8a7ca3e8898514bbb1b56ed9996edfc35b4be617`, `OPEN`, non-draft, base
  `main`, `CLEAN`/`MERGEABLE`.
- Drift `8546ae8d..9a9471e3` is only worker_1 status plus the task333 report
  correction that replaces the three stale task299 row-manifest hashes with
  assigned `074500Z` values; `git diff --check` is clean.
- Drift `9a9471e3..6261daaa` is non-material bookkeeping only:
  worker_1 status plus task333 history/task_knowledge. It does not change the
  task333 report, helper, artifact root, metrics, checksums, or boundary
  claims; `git diff --check` is clean.
- `git diff --check origin/main...origin/pr/396`: clean.
- Helper compile from the refreshed PR head: `PASS`.
- Artifact checksum manifest: all 15 entries `OK`.
- Packed shard checksum manifest: all 96 entries `OK`.
- Qwen30B contract validation rc: `0`; log marker:
  `TASK333_QWEN30B_PACKED_CONTRACT=PASS`.
- Split symlink check: 96 symlinks, 0 broken; train 84, valid 6, test 6.
- Intended-vs-exposed parity: `all_pass=true`.

## Corrected Hash Verification

The refreshed #396 report's Source Provenance table at exact head `6261daaa`
matches `run_20260604T074500Z/manifests/source_provenance.json` and direct
`sha256sum` of the row-manifest files.

| Source | Refreshed #396 report | `074500Z` manifest/file |
|---|---|---|
| `m1-agentic-sft-v11-from-m0` | `7562c86407e00c890ba86eb150a28c8c9bfbc1d7d35eb2c43bfbc5a9af878599` | `7562c86407e00c890ba86eb150a28c8c9bfbc1d7d35eb2c43bfbc5a9af878599` |
| `m1-agentic-sft-v11-math-final-answer` | `e466ee7bd8032ff45596073d21c75f482611689edee3a20a9f5ade440a1ac653` | `e466ee7bd8032ff45596073d21c75f482611689edee3a20a9f5ade440a1ac653` |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | `89ab29ebe1ab5a11e4467652ff40a855612e1ef4a47d024bbdc02eb9cd965e2f` | `89ab29ebe1ab5a11e4467652ff40a855612e1ef4a47d024bbdc02eb9cd965e2f` |
| `agentic-interactive` | `81f558b6cd08b9159402aab073283d9cee2898d0b83b23efd71a3a49e6160fbc` | `81f558b6cd08b9159402aab073283d9cee2898d0b83b23efd71a3a49e6160fbc` |
| `instruction-following-structured` | `206e27cb006fce1321115dd68732531cf46f6d3eb7e2d385f0eb3a2e7bb4c7a7` | `206e27cb006fce1321115dd68732531cf46f6d3eb7e2d385f0eb3a2e7bb4c7a7` |
| `swe` | `998a95f209d2863de50b115704493bc7406ce5f37046732f75ab737bc9fa7ab2` | `998a95f209d2863de50b115704493bc7406ce5f37046732f75ab737bc9fa7ab2` |

Old incorrect values are absent from the refreshed report:

- `5894818a7fcfea644e202da10f551f3de844b8369432221c376e5121ef80cd15`
- `ca07a194e74131b726252bd2589a83c0572ef9bb04c426b710032fcbdc1bb521`
- `f1373026c688817a7e47f6060878f975e9bf125e959aee6375bcf49149cf4820`

Correct values are present:

- `7562c86407e00c890ba86eb150a28c8c9bfbc1d7d35eb2c43bfbc5a9af878599`
- `e466ee7bd8032ff45596073d21c75f482611689edee3a20a9f5ade440a1ac653`
- `89ab29ebe1ab5a11e4467652ff40a855612e1ef4a47d024bbdc02eb9cd965e2f`

## Packed Contract Evidence

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
- Decontam/no-forbidden-source proof:
  - `aime2025_prompt_or_label_train_rows`: 0.
  - `task255_reuse`: not used.
  - all nine task327 `BLOCKED_DECONTAM_HIT` sources excluded.
  - task329 zero-supervised SWE excluded and replaced with task331
    no-tools-header SWE.
  - six task332 structured validation-filtered rows excluded fail-closed.
- Task332 split policy is represented: source-local shard 14 valid, shard 15
  test, all other shards train.

## Residual Risks

- No fresh task333 decontam scan was run; task333 carries accepted upstream
  decontam proofs.
- The task299 seed still lacks a normalized-prompt hit field; this is carried
  as a residual rather than newly asserted.
- The hard-math task299 source exposes valid/test shard files with zero rows.
- SWE rows still truncate to 4096 tokens, inherited from task331, but have
  nonzero supervised tokens in the Qwen pack window.
- The combined root is a symlink/materialization contract over accepted
  upstream packed shards, not a task310 release, 30B release, or training pass.
