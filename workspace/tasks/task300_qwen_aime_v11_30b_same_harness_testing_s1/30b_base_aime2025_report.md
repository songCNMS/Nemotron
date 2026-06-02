# task300 30B base AIME2025 report

<!-- METADATA:STATUS=Blocked,ASSIGNEE=intern_nemotron_worker_3,SESSION=2 -->

## Summary

- Task: `task300_qwen_aime_v11_30b_same_harness_testing_s1`
- Branch:
  `intern_nemotron_worker_3/task300_qwen_aime_v11_30b_same_harness_testing_s1`
- Acceptance head: `85a5ba134c486ac36f30b63e9bcae97f51fdc1f6`
- Base main: `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7`
- Lead docs source:
  `origin/intern_nemotron_lead/session1-recovery-task-docs`
  `676d85563e00dfb665b6a911995bd47b4932c370`
- Disposition: `BLOCK_UPSTREAM_TASK298_ROUTE_MISSING`

The exact 30B corrected AIME2025 base score was not produced in this session.
Task300 explicitly depends on task298 for the exact 30B runtime/eval route and
model path. At this snapshot, task298 has a remote acceptance branch but no
runtime/resource/base-load report, no PR, and no artifact root visible from
worker_3. Launching a 30B endpoint/export/eval without that route proof would
violate task300's fail-closed dependency.

## Upstream Gate State

| Gate | Observed state | Task300 effect |
|---|---|---|
| task298 runtime/base-load | Branch `intern_nemotron_worker_2/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1` at `7d24b9295740ef5c21fd443d6399ec9641f8f5c5`; only README/history/task_knowledge visible, no report/artifacts/PR found | Blocks 30B base scoring route |
| task299 data/packing | Branch `intern_nemotron_worker_1/task299_qwen_aime_v11_30b_data_packing_contract_s1` at `ff30fad8e6899b9a98d9530006ef49c52c7d72fb`; only README/history/task_knowledge visible, no report found | Blocks later task301 training validation; not required to score base but still unresolved |
| task301 training/checkpoint | PR #362 open/CLEAN at `b8e42b3e748c8c80cb3c4a938f2db06c9cb0b6d6`; report says `BLOCKED_UPSTREAM_GATES_MISSING` and no checkpoint was produced | Blocks non-AIME canary and FT-vs-base testing |
| task302 review | PR #361 open; runbook disposition `HOLD_WAITING_TASK298_TASK301_EVIDENCE` | Independent review also holds |

## Read-Only Probes

Artifact root:

`/work-agents/intern_nemotron_worker_3/outputs/task300_qwen_aime_v11_30b_same_harness_testing_s1/run_20260602T144005Z`

Commands were read-only and did not launch eval, endpoint, export, canary, or
training.

```bash
ssh NemTron 'set -e; echo HOST=$(hostname); echo PY=$(python3 --version 2>&1); nvidia-smi --query-gpu=index,name,memory.total,memory.used,utilization.gpu --format=csv,noheader; for p in /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Base /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Thinking-2507 /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507-FP8; do if [ -e "$p" ]; then echo PATH_OK:$p; find "$p" -maxdepth 1 -type f -printf "%f %s bytes\n" | sort | head -20; else echo PATH_MISSING:$p; fi; done'
ssh NemTron 'for port in 13000 13147 30000 30001 13157; do echo PORT:$port; timeout 2 curl -sS http://127.0.0.1:${port}/v1/models || true; echo; done'
ssh NemTron 'python3 - <<PY
import importlib
mods = ["sglang", "torch", "transformers", "megatron", "megatron.core"]
for name in mods:
    try:
        mod = importlib.import_module(name)
        print("IMPORT_OK:{}:{}".format(name, getattr(mod, "__version__", "no_version")))
    except Exception as exc:
        print("IMPORT_FAIL:{}:{}:{}".format(name, type(exc).__name__, exc))
PY'
git ls-remote --heads origin '*task298*' '*task299*' '*task300*' '*task301*'
gh pr list --state all --search 'task298 OR task299 OR task300 OR task301' --json number,title,state,headRefName,headRefOid,baseRefName,mergeStateStatus,mergedAt,url --limit 30
```

## Probe Results

- NemTron host: `lg-cmc-b7r201-f08u26-h200-000126`
- Python: `3.12.3`
- GPUs: eight `NVIDIA H200`, each `143771 MiB`; probe saw `1 MiB` used and
  `0 %` utilization on all eight.
- Candidate model path exists:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- Nearby variants also exist:
  - `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Base`
  - `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Thinking-2507`
  - `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507-FP8`
- Import probe:
  - `sglang`: `0.5.8`
  - `torch`: `2.9.1+cu129`
  - `transformers`: `4.57.1`
  - `megatron`: import ok
  - `megatron.core`: `0.16.0rc0`
- No local endpoint was listening on probed common ports:
  `13000`, `13147`, `30000`, `30001`, `13157`.
- Task247 corrected AIME2025 input cache remains available locally for a later
  same-harness base run:
  `c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74`.
- Task247 input source manifest hash:
  `0c68142e83da11107e5dbaa86bfad1dbba87799354853de196c5f2434139b171`.

## Checksums

| Artifact | sha256 |
|---|---|
| `logs/nemtron_30b_path_gpu_probe.log` | `fbbe50534398b9afa075a331247eb7acb744bdb04fd915437968880491f7ae09` |
| `logs/nemtron_endpoint_probe.log` | `d0eb0295776fd2be5bdecd9a4f52344c3fdbb0cbe5c039072966c992b47966d0` |
| `logs/nemtron_import_probe.log` | `4bbb37ae63fb964931aa896f94aa07c1e818fa1c40d07aac59c5b741400ec06d` |
| `logs/remote_branch_probe.log` | `baa3860ec8779ed1c71e19de234e4789dfc9b8b52b90fa50e6d64905729298b4` |
| `logs/github_pr_probe.json` | `36a8e3a31f63ccf4d8d98cd42716874479ffcf96d265fc5e0005def390d2f5e0` |

## Base Score Status

- Full completions: not produced.
- Parser diagnostics: not produced.
- Numerator/denominator: not produced.
- Exact-normalized base accuracy: not produced.
- Reason: task298 has not yet provided the required 30B runtime/eval route
  proof. Starting an endpoint/export or corrected AIME eval before that proof
  would exceed task300's dependency contract.

## Next Allowed Step

Wait for task298 to publish a PASS runtime/resource/base-load route or exact
blocker with model path, required resources, parallelism, endpoint/export
decision, and artifact checksums. If task298 approves an eval route, task300 can
run the exact 30B base corrected AIME2025 score using the task247 corrected
AIME cache/protocol, retaining full completions, parser diagnostics, checksums,
and all-request denominator.

After task301 produces a checkpoint and task299 data/decontam proof is accepted,
task300 must run the non-AIME canary before any corrected AIME2025 FT-vs-base
comparison.

## Boundary Confirmation

Confirmed:

- No training or optimizer steps.
- No task255 reuse.
- No AIME2025 prompts or labels as trainable data.
- No corrected AIME scoring was launched.
- No non-AIME canary was launched.
- No export or conversion.
- No endpoint launch.
- No promotion or 30B scale decision beyond this blocked testing report.
- No shared deletion.
- No main push or merge.
