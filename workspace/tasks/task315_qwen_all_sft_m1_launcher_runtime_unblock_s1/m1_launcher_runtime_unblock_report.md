# task315 M1 Launcher Runtime Unblock Report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_2,SESSION=2 -->

## Disposition

`BLOCK_RUNTIME`.

Task315 did not find a currently safe local/NemTron/LTP route that can run M1
launcher rows without additional lead-gated runtime work. Fourteen M1 rows have
exact launcher mappings in the repo, but the current worker runtime lacks
`nemo-evaluator-launcher`, `nemo-evaluator`, benchmark modules, scheduler
support, and a working Docker daemon. The historical task225 venv has
`nemo-evaluator-launcher==0.2.5` and `nemo-evaluator==0.2.8`, but still lacks
the benchmark modules needed by the mapped rows and does not solve the missing
container/scheduler route.

Five M1 rows remain exact-task unavailable in the approved launcher mapping:
`multichallenge`, `terminalbench`, `mcp_mark`, `tool_decathlon`, and
`swe_bench_verified`. Candidate tasks such as MT-Bench, codec contamination
checks, ToolTalk, and BFCL variants are not equivalent substitutes.

Recommended next gate:
`RUNTIME_REMEDIATION_REQUIRED_BEFORE_M1_ROWS`. A later lead-gated task may
either provide a task-owned launcher environment with benchmark modules plus a
working container/scheduler route, or revalidate the historical vm4vpn route
with current credentials, endpoint tunnel, Docker access, and row-specific
credentials. No benchmark row should run from this report alone.

## Run Identity

- Worker branch:
  `intern_nemotron_worker_2/task315_qwen_all_sft_m1_launcher_runtime_unblock_s1`
- PR: to be opened from this branch.
- Branch base:
  `origin/main` `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Acceptance head:
  `14d90bc3784c4564259339910fb3507979583897`
- Lead task docs:
  `origin/intern_nemotron_lead/session1-recovery-task-docs`
  `f1f5efabbff34eae735b1f5b536293c49a5853d9`
- Task311 review target:
  #371 head `9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6`
- Host:
  `lg-cmc-b7r201-n09u29-cpu-000191`
- User:
  `uid=0(root) gid=0(root) groups=0(root)`
- Python:
  `/usr/bin/python3`
- Task-owned output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task315_qwen_all_sft_m1_launcher_runtime_unblock_s1/run_20260603T190821Z`

## Probe Commands And Environment

The probes were read-only except for task-owned output writes under the task315
output root.

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git checkout -B intern_nemotron_worker_2/task315_qwen_all_sft_m1_launcher_runtime_unblock_s1 origin/main
```

Runtime command and package inventory:

```bash
command -v nemo-evaluator-launcher nemo-evaluator docker sbatch srun singularity apptainer enroot ltp
docker --version
sbatch --version
srun --version
singularity --version
apptainer --version
enroot version
python3 - <<'PY'
import importlib.metadata as md
for name in [
    "nemo-evaluator-launcher", "nemo-evaluator", "lm-eval",
    "simple-evals", "nemo-skills", "bfcl-eval", "tau2-bench",
]:
    try:
        print("DIST", name, md.version(name))
    except Exception as exc:
        print("DIST", name, "MISSING", type(exc).__name__ + ":", exc)
PY
```

Python import probes:

```bash
/usr/bin/python3 - <<'PY'
import importlib, json, sys
mods = [
    "nemo_evaluator_launcher", "nemo_evaluator",
    "nemo_evaluator_launcher.api", "lm_eval", "simple_evals",
    "nemo_skills", "bfcl_eval", "tau2_bench", "hle",
    "livecodebench", "scicode", "ifbench", "ruler", "datasets", "yaml",
]
rows = []
for mod in mods:
    try:
        imported = importlib.import_module(mod)
        rows.append({"module": mod, "import": "PASS", "file": getattr(imported, "__file__", None)})
    except Exception as exc:
        rows.append({"module": mod, "import": "FAIL", "error": type(exc).__name__ + ": " + str(exc)})
print("PYTHON", sys.executable)
print(json.dumps(rows, indent=2, sort_keys=True))
PY

/work-agents/.venv/bin/python - <<'PY'
# same import probe; this failed because /work-agents/.venv/bin/python is missing
PY

/mnt/cephfs/data/processing/nemotron-live-validation/task225/runtime_venv/bin/python - <<'PY'
# same import probe against historical task225 runtime_venv
PY
```

Historical launcher and container probes:

```bash
/mnt/cephfs/data/processing/nemotron-live-validation/task225/runtime_venv/bin/nemo-evaluator-launcher --help
/mnt/cephfs/data/processing/nemotron-live-validation/task225/runtime_venv/bin/nemo-evaluator-launcher version
/mnt/cephfs/data/processing/nemotron-live-validation/task225/runtime_venv/bin/nemo-evaluator-launcher ls --help
find /mnt/cephfs/data/processing/nemotron-live-validation/task225 -maxdepth 4 -name '*nemo_evaluator_launcher*' -o -name 'nemo-evaluator-launcher'
docker ps
sha256sum \
  /mnt/cephfs/data/processing/nemotron-live-validation/task231/logs/runtime_inventory.log \
  /mnt/cephfs/data/processing/nemotron-live-validation/task231/probes/new_runtime_mapping_scan.json
```

Row feasibility matrix generation used the repo configs:

```bash
python3 - <<'PY'
# Load and compare:
# - src/nemotron/recipes/super3/stage3_eval/config/m1_full_basket.yaml
# - src/nemotron/recipes/super3/stage3_eval/config/m1_full_basket_launcher_available.yaml
# - src/nemotron/recipes/super3/milestones/m1_eval_basket/m1_eval_launcher_mapping.yaml
# Write probes/row_matrix_probe.json
PY
sha256sum logs/* manifests/* probes/*
```

## Artifact Manifest

| Artifact | sha256 |
|---|---|
| `logs/local_command_probe.log` | `a531ef9704732b5ea5c9f8e192c456a88e48cab177eb6d7ae978eea0db44076c` |
| `logs/local_python_import_probe.log` | `531a0b490ae5b46f068ff1e85e0c7daf82b1b5f83102d2aad400ecab79303539` |
| `logs/work_agents_venv_import_probe.log` | `1a7293113d1cda67296a0700769b621dc9e8c4aac585dd3c89705a829a48d2ac` |
| `logs/task225_runtime_import_probe.log` | `fea096af042a377296d904ddbef23155449f4958143bf4c3cc4529f0c0acd088` |
| `logs/task225_launcher_help.log` | `8b41ba798118f7da38b8f8701dc8c2c0905f2fa731ffefb3360f709a6344e4d3` |
| `logs/task225_launcher_version.log` | `e9da781ab77663f8c29d17a90bae6e3de6b4a4da3324fecee41f5309d2b1bb3f` |
| `logs/task225_launcher_ls_help.log` | `d1ce8b6ca85c53f4031d4f80cc74de7761ce28c8e14c9b3fa3ad8869f04b15b9` |
| `logs/task225_resource_find.log` | `ef79185a6c64a7c45e668cabed1f719f5737a1c37298b224ad07a67b38ff110c` |
| `logs/docker_ps.log` | `1386e7544f6712b4e0727f9b0642b4a73d168b0753dc2a1454ab9d23dbb57ff1` |
| `manifests/run_identity.txt` | `71b3c5d3a0ddf2d271472464a7cae5beab0cb8be94d9850120319ad82ef88ec8` |
| `manifests/file_inventory.txt` | `83ce536d87a9781db4380f08612dd60fea11cd2461f51af3294a658c8d74defe` |
| `manifests/prior_launcher_artifact_hashes.sha256` | `6cc2856c5fca2154f1773d51d5d5c33755f0cdb5ef16c50a3bf9cfb8fbebf711` |
| `probes/row_matrix_probe.json` | `132c2910c56323a99070909fa61a3d5c83fa4c2830975750735bb27efbfb389a` |

Task231 prior artifact hashes reproduced:

| Prior artifact | sha256 |
|---|---|
| `/mnt/cephfs/data/processing/nemotron-live-validation/task231/logs/runtime_inventory.log` | `dc3067435820265879200dc93a508cba70f8abfe2c00cc7c080f1193c885bfba` |
| `/mnt/cephfs/data/processing/nemotron-live-validation/task231/probes/new_runtime_mapping_scan.json` | `ed8aa2fc82f77214fd11f31a223f9835baf94f50fdf95bcb1720e93a56276610` |

Full checksum manifest:
`/work-agents/intern_nemotron_worker_2/outputs/task315_qwen_all_sft_m1_launcher_runtime_unblock_s1/run_20260603T190821Z/manifests/artifact_checksums.sha256`.

## Runtime Findings

| Route | Current evidence | Decision |
|---|---|---|
| Default worker Python | Missing `nemo_evaluator_launcher`, `nemo_evaluator`, `lm_eval`, `simple_evals`, `nemo_skills`, `bfcl_eval`, `tau2_bench`, `hle`, `livecodebench`, `scicode`, `ifbench`, and `ruler`; `datasets` and `yaml` import. | `BLOCK_RUNTIME` |
| `/work-agents/.venv` | `/work-agents/.venv/bin/python` missing. | `BLOCK_RUNTIME` |
| Historical task225 venv | `nemo-evaluator-launcher==0.2.5` and `nemo-evaluator==0.2.8` import and CLI help/version pass; benchmark modules remain missing. | `PARTIAL_LAUNCHER_ONLY_NOT_RUNNABLE` |
| Docker on worker host | `docker` client exists, but `docker ps` fails: cannot connect to `/var/run/docker.sock`. | `BLOCK_CONTAINER_RUNTIME` |
| Scheduler/container alternatives | `sbatch`, `srun`, `singularity`, `apptainer`, and `enroot` are missing. | `BLOCK_SCHEDULER_OR_ALT_CONTAINER` |
| LTP/OpenPAI | No current task-owned command/credential route validated by this task. | `BLOCK_CREDENTIAL_OR_ROUTE_UNVALIDATED` |
| Historical vm4vpn route | Task071 records that this can work only after external Docker permission and SSH tunnel setup; this task did not validate current access, credentials, endpoint, or row credentials. | `LEAD_GATED_REVALIDATION_REQUIRED` |

## Row Feasibility Matrix

Summary:

- Total intended M1 rows: `19`
- Exact launcher mappings present: `14`
- Exact task mappings missing/unavailable: `5`
- Runnable now in current task315 local/NemTron/LTP state: `0`

| Benchmark | Launcher task | Current task315 feasibility | Blocker |
|---|---|---|---|
| `mmlu_pro` | `lm-evaluation-harness.mmlu_pro` | `ROUTE_PLAN_AFTER_TASK_OWNED_RUNTIME_SETUP` | exact mapping exists; launcher/container/modules absent |
| `aime25` | `simple_evals.AIME_2025` | `ROUTE_PLAN_AFTER_TASK_OWNED_RUNTIME_SETUP` | exact mapping exists; launcher/container/modules absent; no row authorized |
| `hmmt` | `nemo_skills.ns_hmmt_feb2025` | `ROUTE_PLAN_AFTER_TASK_OWNED_RUNTIME_SETUP` | exact mapping exists; `nemo_skills` absent |
| `gpqa` | `simple_evals.gpqa_diamond` | `ROUTE_PLAN_AFTER_TASK_OWNED_RUNTIME_SETUP` | exact mapping exists; `simple_evals` absent; HF access may be needed |
| `hle` | `hle.hle` | `ROUTE_PLAN_AFTER_TASK_OWNED_RUNTIME_SETUP` | exact mapping exists; `hle` absent; HLE may need HF gated dataset and judge/API credentials |
| `livecodebench` | `livecodebench.codegeneration_release_latest` | `ROUTE_PLAN_AFTER_TASK_OWNED_RUNTIME_SETUP` | exact mapping exists; `livecodebench` absent; prior route has OOM/disk risk |
| `scicode` | `scicode.scicode` | `ROUTE_PLAN_AFTER_TASK_OWNED_RUNTIME_SETUP` | exact mapping exists; `scicode` absent; endpoint context may matter later |
| `ifbench` | `ifbench.ifbench` | `ROUTE_PLAN_AFTER_TASK_OWNED_RUNTIME_SETUP` | exact mapping exists; `ifbench` absent; launcher container route required |
| `multichallenge` | N/A | `UNAVAILABLE_EXACT_TASK_MISSING` | no exact safe launcher task; `mtbench.mtbench-cor1` is not equivalent |
| `ruler_256k` | `ruler.ruler-256k-chat` | `BLOCKED_BY_RUNTIME_PLUS_CONTEXT_REQUIREMENT` | exact mapping exists; `ruler` absent; 256k context requirement |
| `aa_lcr` | `AA-LCR.aa_lcr` | `ROUTE_PLAN_AFTER_TASK_OWNED_RUNTIME_SETUP` | exact mapping exists; launcher/container/modules absent; long-context risk |
| `taubench_airline` | `tau2_bench.tau2_bench_airline` | `BLOCKED_BY_RUNTIME_PLUS_MODULE_OR_CREDENTIAL_RISK` | exact mapping exists; `tau2_bench` absent; runtime and possible credential/data risk |
| `terminalbench` | N/A | `UNAVAILABLE_EXACT_TASK_MISSING` | `codec.terminalbench` is contamination detector context, not a benchmark substitute |
| `bfcl` | `bfcl.bfclv3` | `BLOCKED_BY_RUNTIME_PLUS_MODULE_OR_CREDENTIAL_RISK` | exact mapping exists; `bfcl_eval` absent; executable categories may need external API keys |
| `mcp_mark` | N/A | `UNAVAILABLE_EXACT_TASK_MISSING` | no exact task found |
| `tool_decathlon` | N/A | `UNAVAILABLE_EXACT_TASK_MISSING` | `tooltalk.tooltalk` and `bfcl.bfclv3_ast_prompting` are not equivalent |
| `swe_bench_verified` | N/A | `UNAVAILABLE_EXACT_TASK_MISSING` | `codec.swebench_test` is contamination detector context, not SWE-Bench Verified eval |
| `mmlu_prox` | `lm-evaluation-harness.mmlu_prox_chat` | `ROUTE_PLAN_AFTER_TASK_OWNED_RUNTIME_SETUP` | exact mapping exists; launcher/container/modules absent; context risk later |
| `wmt24pp` | `nemo_skills.ns_wmt24pp` | `BLOCKED_BY_RUNTIME_PLUS_MODULE_OR_CREDENTIAL_RISK` | exact mapping exists; `nemo_skills` absent; runtime and data/module setup needed |

## Smallest Remediation Path

No remediation is authorized by this task. If lead releases a follow-up, the
smallest defensible route is:

1. Create a task-owned launcher runtime, not a shared mutation, with
   `nemo-evaluator-launcher`, `nemo-evaluator`, and the benchmark packages for
   the selected first row.
2. Provide a working client execution backend: Docker daemon access,
   Slurm-backed launcher route, or another explicit container/scheduler route.
3. If using vm4vpn, revalidate current Docker group access, current SSH tunnel
   from the evaluator host to the model endpoint, and endpoint reachability from
   inside eval-factory containers.
4. Before any row run, confirm row-specific credentials and constraints:
   HLE/HF/judge credentials, BFCL executable API keys, TauBench data/API needs,
   and long-context feasibility for RULER/AA-LCR/MMLU-ProX.
5. Start with a single lead-approved, non-benchmark-row dry-run or one
   explicitly released minimal row. Do not infer full basket readiness from
   package import alone.

## Residual Risks

- The historical task071 vm4vpn route may still be viable, but task315 did not
  validate current credentials, current endpoint tunnel, or current Docker
  permissions.
- The task225 venv is shared historical state and is incomplete for M1 rows.
  It should not be treated as a task-owned launcher environment.
- Exact missing mappings remain a benchmark-definition issue, not just a
  runtime issue.
- Long-context and external credential rows can still block after launcher
  runtime remediation.

## Boundary Confirmation

Confirmed:

- No benchmark rows were run.
- No training, optimizer step, packing, export, endpoint, promotion, or merge
  was run.
- No task255 reuse.
- No AIME2025 train data use.
- No shared file deletion, including under `/mnt/cephfs/data/processing/lei.song`.
- No system package install/uninstall or shared runtime mutation.
- No main push.
