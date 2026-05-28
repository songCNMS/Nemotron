# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Eval command implementation for super3 recipe (stage3).

This module defines the `eval` command with **visible execution logic**.
Unlike training commands, the evaluator calls nemo-evaluator-launcher
directly instead of submitting a script via nemo-run.

There is no recipe script and no [tool.runspec] block -- the evaluator
is a different execution pattern.

Design: LLM-Native Recipe Architecture
- Execution logic visible and modifiable
- Fork this file to change how evaluations are submitted
"""

from __future__ import annotations

from pathlib import Path

import typer
from omegaconf import DictConfig, OmegaConf, open_dict
from rich.console import Console

from nemo_runspec.config import (
    build_job_config,
    clear_artifact_cache,
    parse_config,
    register_resolvers_from_config,
)
from nemo_runspec.display import display_job_config, display_job_submission
from nemo_runspec.env import parse_env
from nemo_runspec.evaluator import (
    ensure_wandb_host_env,
    get_non_task_args,
    inject_wandb_env_mappings,
    maybe_auto_squash_evaluator,
    needs_wandb,
    parse_task_flags,
    save_eval_configs,
)
from nemo_runspec.recipe_config import RecipeConfig, parse_recipe_config
from nemo_runspec.recipe_typer import RecipeMeta

console = Console()

# =============================================================================
# Recipe Metadata (no SPEC -- evaluator has no recipe script)
# =============================================================================

CONFIG_DIR = "src/nemotron/recipes/super3/stage3_eval/config"

META = RecipeMeta(
    name="super3/eval",
    script_path="",  # No recipe script
    config_dir=CONFIG_DIR,
    default_config="default",
    input_artifacts={"model": "Model checkpoint to evaluate"},
    output_artifacts={},
)


# =============================================================================
# Execution Logic
# =============================================================================


def _as_task_entry(task):
    """Normalize a compact task selector into launcher task-entry shape."""
    if isinstance(task, str):
        return {"name": task}
    return task


def load_stage3_eval_config(ctx, config_dir: Path, default_config: str) -> DictConfig:
    """Load a stage3 eval config and expand compact basket overlays.

    ``m1_basket.yaml`` and ``m1_full_basket*.yaml`` use a compact overlay:

    defaults: default.yaml
    tasks:
      - benchmark.task

    ``nemo_runspec.config.parse_config`` intentionally loads one YAML file
    and does not implement this recipe-local inheritance convention. Expand it
    here so basket configs inherit the full evaluator launcher schema and map
    top-level ``tasks`` into ``evaluation.tasks``.
    """
    config = parse_config(ctx, config_dir, default_config)
    defaults = config.get("defaults")

    if isinstance(defaults, str):
        base_path = config_dir / defaults
        base = OmegaConf.load(base_path)
        overlay = OmegaConf.create(OmegaConf.to_container(config, resolve=False))
        del overlay["defaults"]
        config = OmegaConf.merge(base, overlay)

    if "tasks" in config:
        task_entries = [_as_task_entry(task) for task in config.tasks]
        if "evaluation" not in config:
            config.evaluation = {}
        config.evaluation.tasks = task_entries
        del config["tasks"]

    return config


def _ensure_mapping(cfg, *keys: str):
    current = cfg
    for key in keys:
        if key not in current or current[key] is None:
            with open_dict(current):
                current[key] = {}
        current = current[key]
    return current


def _merge_env_vars(target, source) -> None:
    if not source:
        return
    for key, value in source.items():
        if key not in target or target[key] is None:
            with open_dict(target):
                target[key] = value


def normalize_evaluator_launcher_config(config: DictConfig) -> None:
    """Normalize repo eval configs for current nemo-evaluator-launcher.

    Launcher 0.2.5 rejects the older ``execution.env_vars`` layout. Move those
    entries to the scope-specific locations accepted by the launcher and select
    sequential local execution for generic deployments, which cannot run in
    the launcher's default parallel mode.
    """
    if "execution" in config and "env_vars" in config.execution:
        execution_env_vars = config.execution.env_vars

        if "deployment" in execution_env_vars:
            target = _ensure_mapping(config, "deployment", "env_vars")
            _merge_env_vars(target, execution_env_vars.deployment)

        if "evaluation" in execution_env_vars:
            target = _ensure_mapping(config, "evaluation", "env_vars")
            _merge_env_vars(target, execution_env_vars.evaluation)

        if "export" in execution_env_vars:
            target = _ensure_mapping(config, "env_vars")
            _merge_env_vars(target, execution_env_vars.export)

        with open_dict(config.execution):
            del config.execution["env_vars"]

    if (
        config.get("execution", {}).get("type") == "local"
        and config.get("deployment", {}).get("type") == "generic"
        and "mode" not in config.execution
    ):
        with open_dict(config.execution):
            config.execution.mode = "sequential"

    if "corrected_math" in config:
        with open_dict(config):
            del config["corrected_math"]

    if "qwen_chat_contract" in config:
        with open_dict(config):
            del config["qwen_chat_contract"]

    if "defaults" in config:
        with open_dict(config):
            del config["defaults"]


def _execute_eval(cfg: RecipeConfig):
    """Execute evaluation with nemo-evaluator-launcher.

    This function contains the VISIBLE execution logic. Unlike training
    commands, the evaluator calls run_eval() directly instead of nemo-run.

    Args:
        cfg: Parsed recipe configuration
    """
    # --stage is not supported for evaluator
    if cfg.stage:
        typer.echo("Error: --stage is not supported for evaluator commands", err=True)
        raise typer.Exit(1)

    # =========================================================================
    # 1. Parse configuration
    # =========================================================================
    config_dir = Path(CONFIG_DIR)
    train_config = load_stage3_eval_config(cfg.ctx, config_dir, "default")
    env = parse_env(cfg.ctx)

    # Build full job config with provenance
    job_config = build_job_config(
        train_config,
        cfg.ctx,
        "super3/eval",
        "",  # No script path
        cfg.argv,
        env_profile=env,
    )

    # =========================================================================
    # 2. Auto-inject W&B env mappings if W&B export is configured
    # =========================================================================
    if needs_wandb(job_config):
        inject_wandb_env_mappings(job_config)
    normalize_evaluator_launcher_config(job_config)

    # =========================================================================
    # 3. Auto-squash container images for Slurm execution
    # =========================================================================
    maybe_auto_squash_evaluator(
        job_config,
        mode=cfg.mode,
        dry_run=cfg.dry_run,
        force_squash=cfg.force_squash,
    )

    # =========================================================================
    # 4. Display compiled configuration
    # =========================================================================
    for_remote = cfg.mode in ("run", "batch")
    display_job_config(job_config, for_remote=for_remote)

    # Handle dry-run mode
    if cfg.dry_run:
        return

    # =========================================================================
    # 5. Save configs (job.yaml for provenance, eval.yaml for launcher)
    # =========================================================================
    job_path, eval_path = save_eval_configs(
        job_config, "super3/eval", for_remote=for_remote
    )

    # Display job submission summary
    display_job_submission(job_path, eval_path, {}, cfg.mode, artifacts=job_config.get("artifacts"))

    # =========================================================================
    # 6. Execute via evaluator launcher
    # =========================================================================

    # Ensure W&B host env vars BEFORE artifact resolution
    ensure_wandb_host_env()

    # Resolve artifacts (${art:model,path} etc.)
    clear_artifact_cache()
    register_resolvers_from_config(
        job_config,
        artifacts_key="run",
        mode="pre_init",
    )

    # Resolve all interpolations
    resolved_config = OmegaConf.to_container(job_config, resolve=True)

    # Extract evaluator-specific config (everything except 'run' section)
    eval_config = {k: v for k, v in resolved_config.items() if k != "run"}
    eval_config = OmegaConf.create(eval_config)

    # Parse -t/--task flags from passthrough
    task_list = parse_task_flags(cfg.passthrough)

    # Validate that no extra passthrough args exist (only -t/--task allowed)
    extra_args = get_non_task_args(cfg.passthrough)
    if extra_args:
        typer.echo(
            f"Error: Unknown arguments: {' '.join(extra_args)}\n"
            "Only -t/--task flags are supported for passthrough.",
            err=True,
        )
        raise typer.Exit(1)

    # Import and call evaluator launcher
    try:
        from nemo_evaluator_launcher.api.functional import run_eval
    except ImportError:
        typer.echo(
            "Error: nemo-evaluator-launcher is required for evaluation", err=True
        )
        typer.echo('Install with: pip install "nemotron[evaluator]"', err=True)
        raise typer.Exit(1)

    # Inject W&B env var mappings into eval_config if needed
    if needs_wandb(eval_config):
        inject_wandb_env_mappings(eval_config)
    normalize_evaluator_launcher_config(eval_config)

    # Call the launcher
    console.print("\n[bold blue]Starting evaluation...[/bold blue]")
    invocation_id = run_eval(eval_config, dry_run=False, tasks=task_list)

    if invocation_id:
        console.print(
            f"\n[green]\u2713[/green] Evaluation submitted: [cyan]{invocation_id}[/cyan]"
        )
        console.print(
            f"[dim]Check status: nemo-evaluator-launcher status {invocation_id}[/dim]"
        )
        console.print(
            f"[dim]Stream logs: nemo-evaluator-launcher logs {invocation_id}[/dim]"
        )


# =============================================================================
# CLI Entry Point
# =============================================================================


def eval(ctx: typer.Context) -> None:
    """Run evaluation with NeMo-Evaluator (stage3).

    Evaluates the trained model using nemo-evaluator-launcher.
    By default, evaluates the RL stage output (run.model=rl:latest).

    Examples:
        # Eval on cluster (loads env.toml profile)
        nemotron super3 eval --run MY-CLUSTER

        # Override model artifact
        nemotron super3 eval --run MY-CLUSTER run.model=sft:v2

        # Filter specific tasks
        nemotron super3 eval --run MY-CLUSTER -t adlr_mmlu -t hellaswag

        # Dry run (show resolved config without executing)
        nemotron super3 eval --run MY-CLUSTER --dry-run

        # Local execution
        nemotron super3 eval execution.type=local
    """
    cfg = parse_recipe_config(ctx)
    _execute_eval(cfg)
