# task252_qwen_aime_task251_hotpotqa_pr_review_s1 - task251 PR review/test

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_4,SESSION=0 -->

## Background

task251 produced PR #328 to unblock the HotpotQA M0 loader by adding
`local_jsonl_files` support and a task-owned HotpotQA standard-format cache
builder/report. The lead must not run implementation tests directly, so an
independent worker review is required before any approve/request-changes
decision.

Current PR state at assignment:

- PR: `https://github.com/songCNMS/Nemotron/pull/328`
- Base: `main`
- Head branch:
  `intern_nemotron_worker_2/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1`
- Head SHA: `694197c81720dcc157518d8a86b2b5d7a7a2dd05`
- Mergeability: `CLEAN` at lead check time.

## Goal

Independently review and test PR #328 for correctness, scope, reproducibility,
and Qwen AIME25 boundary compliance.

## Scope

- Review the PR diff at exact head
  `694197c81720dcc157518d8a86b2b5d7a7a2dd05`.
- Verify the `prepare_m0_assets.py` `local_jsonl_files` path does not invoke
  the unsupported HotpotQA `trust_remote_code` loader.
- Verify the new test coverage is targeted and meaningful.
- Inspect task251 report evidence for:
  - HotpotQA source revision;
  - cache and registry override paths;
  - row counts and split mapping;
  - checksums;
  - commands/environment/log paths;
  - M0/M1 pass/fail;
  - the current Qwen packing `cosmos_xenna` blocker.
- Confirm the report preserves the global gate:
  no FT checkpoint/export/live eval, no task243 comparison, no promotion, and
  no 30B/8-GPU clearance.

## Suggested Checks

Run focused tests as appropriate from a local checkout of PR #328 head:

```bash
python -m pytest tests/recipes/super3/test_m0_data_env.py -k local_jsonl_override
```

If the focused test cannot run, report the exact environment/blocker. Do not
fix code or modify the worker_2 branch.

## Boundaries

- Do not edit code, commit, push, open PRs, merge, or rewrite worker_2's branch.
- Do not train, run FT eval, run task243 comparison, or launch 30B/8-GPU.
- Do not delete or overwrite shared files under
  `/mnt/cephfs/data/processing/lei.song`.
- Do not treat local artifacts as promotion evidence.

## Expected Output

- Mailbox report to `intern_nemotron_lead` with:
  - PR head SHA tested/reviewed;
  - commands run and pass/fail results;
  - artifact/report checks performed;
  - approve/request-changes/block recommendation;
  - residual risks and untested surfaces.

## Acceptance Criteria

- The review explicitly covers PR #328 head
  `694197c81720dcc157518d8a86b2b5d7a7a2dd05`.
- The review states whether the HotpotQA loader blocker is solved for M0/M1
  prep without AIME25 leakage.
- The review states whether the `cosmos_xenna` packing blocker is correctly
  classified as the next local-prep dependency blocker.
- The review states whether #328 is safe to approve as a local-prep unblock
  report/code PR while keeping the global gate `NO-GO/HOLD`.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Related task: `task251_qwen_aime_v10_hotpotqa_loader_unblock_s1`
- Related PR: `#328`
- First gate: independent review/test report only; no merge authority.
