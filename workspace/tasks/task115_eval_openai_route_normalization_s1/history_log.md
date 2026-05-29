# task115_eval_openai_route_normalization_s1 history

<!-- METADATA:SESSION=17 -->

## Session 16 - 2026-05-29

- Synced branch
  `intern_nem_dev_3/task115_eval_openai_route_normalization_s1` from
  `origin/main` at `d64cbd067a15cca222b9eba200af1eb1ec5b7788`.
- Removed trailing slashes from Super3 and Nano3 Stage3 eval default
  `deployment.endpoints.chat` and `deployment.endpoints.completions`.
- Added focused tests for Super3 default routes, Nano3 default routes, and
  Super3 basket configs inheriting slashless default routes.
- Verified focused pytest, py_compile, Ruff, static route probes, and
  `git diff --check` before staging.
- Opened PR #221 to `main`: https://github.com/songCNMS/Nemotron/pull/221.

## Session 17 - 2026-05-29

- Transitioned from completed task115 PR #221 to PM-assigned
  `task117_qwen_eval_gate_slashless_route_contract_s1` on branch
  `intern_nem_dev_3/task117_qwen_eval_gate_slashless_route_contract_s1`.
- Left task115 implementation unchanged; task117 extends the Qwen eval repro
  gate to enforce the slashless completions-route contract.
