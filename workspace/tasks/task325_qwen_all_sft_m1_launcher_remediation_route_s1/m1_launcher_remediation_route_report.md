# task325 M1 Launcher Remediation Route Report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_3,SESSION=1 -->

## Disposition

`BLOCK_RUNTIME_CONFIRMED`.

I did not find a currently safe route to run M1 launcher rows under the
task325 boundaries. This confirms task315's accepted `BLOCK_RUNTIME` result:
the current worker runtime lacks the launcher/evaluator packages, benchmark
modules, and a working container/scheduler route. Fourteen M1 rows still have
exact launcher mappings in the repo, but `0/19` rows are runnable now.

Task325 also identifies a concrete later remediation route:
`LEAD_GATED_EVAL_ONLY_CONTAINER_OR_SCHEDULER_ROUTE_REQUIRED`. A future task can
attempt a task-owned launcher environment plus a working Docker/Slurm/alternate
container backend, or revalidate the historical vm4vpn-style Docker plus
SSH-tunnel route, before any benchmark row execution.

No benchmark row was run.

## Run Identity

| Field | Value |
| --- | --- |
| Worker branch | `intern_nemotron_worker_3/task325_qwen_all_sft_m1_launcher_remediation_route_s1` |
| Branch base | `origin/main` `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb` |
| Lead docs | `origin/intern_nemotron_lead/session1-recovery-task-docs` `7055dac63c772ac8a317454bffead4a469a0112f` |
| Reviewed task315 branch | `origin/intern_nemotron_worker_2/task315_qwen_all_sft_m1_launcher_runtime_unblock_s1` `89cc7f74a737f174f4b8dbf9129c712fabbafa95` |
| Reviewed task321 branch | `origin/intern_nemotron_worker_4/task321_qwen_all_sft_closeout_merge_runbook_s1` `a908b81dd6583976b08896c8193ca302909c52ff` |
| Task-owned output root | `/work-agents/intern_nemotron_worker_3/outputs/task325_qwen_all_sft_m1_launcher_remediation_route_s1/run_20260603T203449Z` |
| Host | `lg-cmc-b7r201-n09u29-cpu-000191` |
| Python | `/usr/bin/python3` |

## Evidence Reviewed

- Task315 report:
  `workspace/tasks/task315_qwen_all_sft_m1_launcher_runtime_unblock_s1/m1_launcher_runtime_unblock_report.md`
  from worker_2 branch `89cc7f74a737f174f4b8dbf9129c712fabbafa95`.
- Task315 accepted gate state: `APPROVE_BLOCKER_DOCS / BLOCK_RUNTIME`, with
  task315 knowledge recording lead comment `issuecomment-4615943606`.
- Task321 runbook:
  `workspace/tasks/task321_qwen_all_sft_closeout_merge_runbook_s1/closeout_merge_runbook_report.md`
  from worker_4 branch `a908b81dd6583976b08896c8193ca302909c52ff`.
- Repo M1 mapping:
  `src/nemotron/recipes/super3/milestones/m1_eval_basket/m1_eval_launcher_mapping.yaml`.
- Repo launcher subset:
  `src/nemotron/recipes/super3/stage3_eval/config/m1_full_basket_launcher_available.yaml`.

## Probe Commands

The following probes were read-only except for task-owned output writes under
the task325 output root. They did not invoke `nemo-evaluator-launcher run`, any
benchmark task, a model endpoint, export, or training.

```bash
git fetch origin \
  refs/heads/intern_nemotron_worker_2/task315_qwen_all_sft_m1_launcher_runtime_unblock_s1:refs/remotes/origin/intern_nemotron_worker_2/task315_qwen_all_sft_m1_launcher_runtime_unblock_s1 \
  refs/heads/intern_nemotron_worker_4/task321_qwen_all_sft_closeout_merge_runbook_s1:refs/remotes/origin/intern_nemotron_worker_4/task321_qwen_all_sft_closeout_merge_runbook_s1

command -v nemo-evaluator-launcher nemo-evaluator docker sbatch srun singularity apptainer enroot ltp
docker --version
docker ps
sbatch --version
srun --version
singularity --version
apptainer --version
enroot version
ltp --version

python3 - <<'PY'
import importlib, importlib.metadata as md
mods = [
    "nemo_evaluator_launcher", "nemo_evaluator",
    "nemo_evaluator_launcher.api", "lm_eval", "simple_evals",
    "nemo_skills", "bfcl_eval", "tau2_bench", "hle",
    "livecodebench", "scicode", "ifbench", "ruler", "datasets", "yaml",
]
dists = [
    "nemo-evaluator-launcher", "nemo-evaluator", "lm-eval",
    "simple-evals", "nemo-skills", "bfcl-eval", "tau2-bench",
]
PY

/mnt/cephfs/data/processing/nemotron-live-validation/task225/runtime_venv/bin/python - <<'PY'
# Same import/version probe against historical task225 runtime_venv.
PY

/mnt/cephfs/data/processing/nemotron-live-validation/task225/runtime_venv/bin/nemo-evaluator-launcher --help
/mnt/cephfs/data/processing/nemotron-live-validation/task225/runtime_venv/bin/nemo-evaluator-launcher version
```

## Artifact Manifest

| Artifact | sha256 |
| --- | --- |
| `logs/local_command_probe.log` | `4ac9ee4f94b6bb95b2dcb99c16a84ae95a69fa83e65390bd104db316479df1a5` |
| `logs/local_python_import_probe.log` | `859bbbdb0af48a697005ba2dfc2d2fd2425e52fc655a66c22f7f04113b7ca721` |
| `logs/task225_launcher_help.log` | `8c32e3228014fafd2bfab9d92f725eaf519774d379f55fbbee85fb90e32f4f6c` |
| `logs/task225_launcher_version.log` | `2e1dfb30dd1f61859e798e04a086f003ff232ce85dbe0251910742c4d55d62d7` |
| `logs/task225_runtime_import_probe.log` | `13222ea81f164ba43dbc0d0714f88bf056bb4c91cf03217177e302dcb70359fd` |
| `manifests/file_inventory.txt` | `c73c150104d38409bf491218749436fea6a4b350dc501eecdc7658b9f40d2d4d` |
| `manifests/run_identity.txt` | `4f108164f80d4ff02ac8b40e1014f58e1a8b8cba8559bdfdc76cd16992d23fee` |
| `probes/row_matrix_probe.json` | `ee8a0fb2066338c9d28fe0ee4e2be0de6c2f312359c993e6fdbac6b193dee078` |

Full checksum manifest:
`/work-agents/intern_nemotron_worker_3/outputs/task325_qwen_all_sft_m1_launcher_remediation_route_s1/run_20260603T203449Z/manifests/artifact_checksums.sha256`.

## Runtime Findings

| Route | Current task325 evidence | Decision |
| --- | --- | --- |
| Default worker Python | `/usr/bin/python3` lacks `nemo_evaluator_launcher`, `nemo_evaluator`, `lm_eval`, `simple_evals`, `nemo_skills`, `bfcl_eval`, `tau2_bench`, `hle`, `livecodebench`, `scicode`, `ifbench`, and `ruler`; only `datasets` and `yaml` passed. | `BLOCK_RUNTIME` |
| Launcher CLI on PATH | `nemo-evaluator-launcher` and `nemo-evaluator` were not found on `PATH`. | `BLOCK_LAUNCHER_MISSING` |
| Historical task225 venv | Imports `nemo_evaluator_launcher`, `nemo_evaluator`, and `nemo_evaluator_launcher.api`; distributions report `nemo-evaluator-launcher==0.2.5` and `nemo-evaluator==0.2.8`; benchmark modules remain missing. | `PARTIAL_LAUNCHER_ONLY_NOT_RUNNABLE` |
| Docker | Docker client exists (`Docker version 20.10.8`), but `docker ps` fails: cannot connect to `/var/run/docker.sock`. | `BLOCK_CONTAINER_DAEMON` |
| Scheduler/container alternatives | `sbatch`, `srun`, `singularity`, `apptainer`, and `enroot` are not installed on the worker host. | `BLOCK_SCHEDULER_OR_ALT_CONTAINER` |
| LTP/OpenPAI local CLI | `ltp` CLI was not found. No task-owned LTP job route was validated by this task. | `BLOCK_ROUTE_UNVALIDATED` |
| Historical vm4vpn route | Task071/task315 describe a possible route only after current Docker access, endpoint tunnel, eval-factory image access, and credentials are revalidated. Task325 did not mutate shared env or launch endpoints, so this remains unvalidated. | `LEAD_GATED_REVALIDATION_REQUIRED` |

## Row Feasibility Matrix

Summary from the repo mapping and task325 probes:

- Intended M1 rows: `19`
- Exact launcher mappings present: `14`
- Exact task mappings missing/unavailable: `5`
- Runnable now under task325/task315 evidence: `0`

| Benchmark | Launcher task | Current status | Exact blocker |
| --- | --- | --- | --- |
| `mmlu_pro` | `lm-evaluation-harness.mmlu_pro` | `BLOCK_RUNTIME_NOW_ROUTE_REQUIRED` | Launcher/container/modules absent. |
| `aime25` | `simple_evals.AIME_2025` | `BLOCK_RUNTIME_NOW_ROUTE_REQUIRED` | Launcher/container/modules absent; no AIME/task243 eval authorized by task325. |
| `hmmt` | `nemo_skills.ns_hmmt_feb2025` | `BLOCK_RUNTIME_NOW_ROUTE_REQUIRED` | `nemo_skills` absent; launcher/container route absent. |
| `gpqa` | `simple_evals.gpqa_diamond` | `BLOCK_RUNTIME_NOW_ROUTE_REQUIRED` | `simple_evals` absent; HF/data access may need later credential proof. |
| `hle` | `hle.hle` | `BLOCK_RUNTIME_NOW_ROUTE_REQUIRED` | `hle` absent; official HLE scoring may need gated HF data and judge/API credentials. |
| `livecodebench` | `livecodebench.codegeneration_release_latest` | `BLOCK_RUNTIME_NOW_ROUTE_REQUIRED` | `livecodebench` absent; prior route carried image/data disk/OOM risk. |
| `scicode` | `scicode.scicode` | `BLOCK_RUNTIME_NOW_ROUTE_REQUIRED` | `scicode` absent; launcher/container route absent. |
| `ifbench` | `ifbench.ifbench` | `BLOCK_RUNTIME_NOW_ROUTE_REQUIRED` | `ifbench` absent; launcher/container route absent. |
| `multichallenge` | N/A | `UNAVAILABLE_EXACT_TASK_MISSING` | No exact MultiChallenge launcher task; MT-Bench is not equivalent. |
| `ruler_256k` | `ruler.ruler-256k-chat` | `BLOCK_RUNTIME_PLUS_CONTEXT` | `ruler` absent; requires a 256k-capable endpoint/route in a later task. |
| `aa_lcr` | `AA-LCR.aa_lcr` | `BLOCK_RUNTIME_PLUS_CONTEXT` | Launcher/container/modules absent; long-context feasibility must be proven later. |
| `taubench_airline` | `tau2_bench.tau2_bench_airline` | `BLOCK_RUNTIME_PLUS_CREDENTIAL_RISK` | `tau2_bench` absent; data/API needs remain unvalidated. |
| `terminalbench` | N/A | `UNAVAILABLE_EXACT_TASK_MISSING` | `codec.terminalbench` is a contamination detector context, not an eval substitute. |
| `bfcl` | `bfcl.bfclv3` | `BLOCK_RUNTIME_PLUS_CREDENTIAL_RISK` | `bfcl_eval` absent; executable categories may need external API keys. |
| `mcp_mark` | N/A | `UNAVAILABLE_EXACT_TASK_MISSING` | No exact MCP-Mark launcher task found. |
| `tool_decathlon` | N/A | `UNAVAILABLE_EXACT_TASK_MISSING` | ToolTalk/BFCL variants are not Tool-Decathlon equivalents. |
| `swe_bench_verified` | N/A | `UNAVAILABLE_EXACT_TASK_MISSING` | `codec.swebench_test` is contamination detector context, not SWE-Bench Verified eval. |
| `mmlu_prox` | `lm-evaluation-harness.mmlu_prox_chat` | `BLOCK_RUNTIME_PLUS_CONTEXT` | Launcher/container/modules absent; context requirements need later route proof. |
| `wmt24pp` | `nemo_skills.ns_wmt24pp` | `BLOCK_RUNTIME_NOW_ROUTE_REQUIRED` | `nemo_skills` absent; launcher/container route absent. |

## Later Remediation Route

No remediation step below is authorized by task325. This is the minimal route to
release in a future lead-gated eval-only task:

1. Create a task-owned evaluator runtime, not a shared mutation, with the
   pinned launcher/evaluator pair and only the benchmark modules required for
   the first released row or row group. Historical compatibility target:
   `nemo-evaluator-launcher==0.2.5` and `nemo-evaluator==0.2.8`.
2. Provide a working execution backend: Docker daemon access on an evaluator
   host, Slurm-backed launcher execution, or another explicit container backend
   such as Singularity/Apptainer/Enroot if lead releases it.
3. If using the historical vm4vpn-style path, revalidate Docker access, eval
   image availability, SSH tunnel from the evaluator host to a task-owned
   eval-only model endpoint, and endpoint reachability from inside launcher
   containers.
4. Use `deployment.type=none` or the equivalent non-promotional external
   endpoint mode only after lead authorizes an eval-only endpoint route.
5. Prove row-specific prerequisites before row execution: HF/data credentials
   for gated data, HLE judge/API credentials, BFCL external API keys for
   executable categories, TauBench data/API requirements, disk/image capacity
   for LiveCodeBench, and context length for RULER/AA-LCR/MMLU-ProX.
6. Start with a lead-released dry-run/import/container reachability gate or one
   explicitly released minimal row. Import success alone is not full-basket
   readiness.

## Exact Blocker

`BLOCK_RUNTIME_CONFIRMED`: task325 cannot run M1 launcher rows without at least
one forbidden or not-yet-released action: installing or mutating runtime
packages, obtaining a working Docker/scheduler/container backend, launching or
connecting to an eval-only endpoint, and supplying row-specific credentials for
some rows. The five missing exact mappings remain unavailable even after runtime
remediation unless equivalent launcher tasks are added.

## Boundary Confirmation

Confirmed:

- No benchmark rows were run.
- No model eval, AIME/task243 eval, export, endpoint, promotion, training, or
  optimizer step was run.
- No task255 reuse.
- No AIME2025 train rows or labels were used.
- No shared file deletion, including under `/mnt/cephfs/data/processing/lei.song`.
- No system package install/uninstall or shared environment mutation.
- No main push, merge, or self-merge.
