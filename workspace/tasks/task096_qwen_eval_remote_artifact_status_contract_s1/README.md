# task096_qwen_eval_remote_artifact_status_contract_s1 - Qwen eval remote artifact status contract

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2,SESSION=9 -->

## Background

PM assigned a static qwen eval reproduction gate follow-up after `main`
reached `90e64c745e6ed905559aacf11125b4d5d3d1f255`. The production
`qwen_eval_repro_gate.yaml` already marks remote raw artifact checks as
`pm_verified`, but the validator still accepted `local_workspace_verified`
for explicit `vm4vpn:` or `vpn:` raw artifact references.

## Goals

- Keep local `main` aligned with `origin/main` at
  `90e64c745e6ed905559aacf11125b4d5d3d1f255` or newer before branching.
- Require `remote_artifact_check.status == "pm_verified"` whenever an
  evidence record has a `vm4vpn:` or `vpn:` raw artifact path.
- Preserve `local_workspace_verified` for genuinely local artifact checks.
- Add focused regression tests for both remote prefixes and the local positive
  case.
- Avoid live artifact access, endpoint calls, cluster jobs, direct `main` push,
  and self-merge.

## Acceptance Criteria

- [x] Branch created from current `origin/main`.
- [x] Remote raw artifact references require `pm_verified`.
- [x] Local artifact validation still permits `local_workspace_verified`.
- [x] Focused pytest, compile, ruff, structured probe, and whitespace checks pass.
- [ ] PR opened to `main`.

