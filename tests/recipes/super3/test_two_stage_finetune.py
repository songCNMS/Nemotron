"""Tests for the two-stage SFT finetune driver (task013 Session 2a).

Covers:

- ``run_two_stage_finetune`` invokes the injected finetune_fn twice
  (Stage A first, Stage B second)
- Stage A is dispatched with the Stage A config path; Stage B with the
  Stage B config path
- Stage A's ``checkpoint.save`` is threaded into Stage B as a Hydra-
  style ``checkpoint.pretrained_checkpoint=...`` CLI override
- Operator-supplied CLI overrides flow into BOTH stage invocations
- YAML validation: Stage A must declare ``step_function`` resolving to
  ``gpt_step``; Stage B must declare ``super3_sample_level_step``
- Tags ride along (``stage-a`` / ``stage-b`` / loss type)
- Error surfaces: missing config / missing checkpoint.save / wrong
  step_function on either side
- Shipped configs: ``stage_a_default.yaml`` + ``stage_b_default.yaml``
  load cleanly + satisfy driver preconditions
"""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


from nemotron.recipes.super3.stage1_sft.two_stage_finetune import (  # noqa: E402
    StageInvocation,
    TwoStageResult,
    run_two_stage_finetune,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
STAGE_A_DEFAULT_PATH = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage1_sft/config/stage_a_default.yaml"
)
STAGE_B_DEFAULT_PATH = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage1_sft/config/stage_b_default.yaml"
)


class _RecordingFinetune:
    """Fake ``run_finetune`` that records every call for assertions.

    Mirrors ``train.run_finetune`` signature
    ``(config_path, recipe_builder, cli_overrides=None, *, tags=None)``.
    """

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def __call__(self, config_path, recipe_builder, cli_overrides=None, *, tags=None) -> None:  # type: ignore[no-untyped-def]
        self.calls.append(
            {
                "config_path": Path(config_path),
                "recipe_builder": recipe_builder,
                "cli_overrides": list(cli_overrides or []),
                "tags": list(tags or []),
            }
        )


def _fake_recipe_builder(_config):  # type: ignore[no-untyped-def]
    """Stand-in for ``_default_recipe_builder`` — driver passes it
    through to the (fake) finetune_fn; never invoked here."""
    return None


def _write_stage_yaml(
    path: Path,
    *,
    step_function: str,
    checkpoint_save: str,
    pretrained_checkpoint: str | None = None,
) -> Path:
    """Synthesize a minimal stage config the driver can read.

    Only fields the driver actually inspects are populated; the rest of
    a real Stage A/B YAML (recipe / dataset / train / model / etc.) is
    irrelevant at the driver layer.
    """
    data: dict = {
        "step_function": step_function,
        "checkpoint": {
            "save": checkpoint_save,
        },
    }
    if pretrained_checkpoint is not None:
        data["checkpoint"]["pretrained_checkpoint"] = pretrained_checkpoint
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


# ---------- Driver dispatch ----------


def test_driver_invokes_finetune_twice_with_correct_config_paths(tmp_path: Path) -> None:
    stage_a = _write_stage_yaml(
        tmp_path / "a.yaml",
        step_function="gpt_step",
        checkpoint_save="/tmp/stage_a_ckpt",
    )
    stage_b = _write_stage_yaml(
        tmp_path / "b.yaml",
        step_function="super3_sample_level_step",
        checkpoint_save="/tmp/stage_b_ckpt",
        pretrained_checkpoint="TWO_STAGE_DRIVER_OVERRIDES_THIS",
    )
    fake = _RecordingFinetune()

    result = run_two_stage_finetune(
        stage_a,
        stage_b,
        finetune_fn=fake,
        recipe_builder=_fake_recipe_builder,
    )

    assert len(fake.calls) == 2
    assert fake.calls[0]["config_path"] == stage_a
    assert fake.calls[1]["config_path"] == stage_b
    assert isinstance(result, TwoStageResult)


def test_driver_threads_stage_a_checkpoint_into_stage_b_overrides(tmp_path: Path) -> None:
    """Plan §5.1's "Stage B starts from Stage A's checkpoint" is the
    core invariant — pin it explicitly."""
    stage_a = _write_stage_yaml(
        tmp_path / "a.yaml",
        step_function="gpt_step",
        checkpoint_save="/checkpoints/stage_a_v1",
    )
    stage_b = _write_stage_yaml(
        tmp_path / "b.yaml",
        step_function="super3_sample_level_step",
        checkpoint_save="/checkpoints/stage_b_v1",
        pretrained_checkpoint="TWO_STAGE_DRIVER_OVERRIDES_THIS",
    )
    fake = _RecordingFinetune()

    run_two_stage_finetune(
        stage_a, stage_b, finetune_fn=fake, recipe_builder=_fake_recipe_builder
    )

    stage_b_overrides = fake.calls[1]["cli_overrides"]
    assert (
        "checkpoint.pretrained_checkpoint=/checkpoints/stage_a_v1"
        in stage_b_overrides
    )


def test_driver_does_not_override_pretrained_checkpoint_in_stage_a(tmp_path: Path) -> None:
    """Only Stage B gets the override — Stage A uses whatever YAML/CLI
    the operator supplied."""
    stage_a = _write_stage_yaml(
        tmp_path / "a.yaml",
        step_function="gpt_step",
        checkpoint_save="/checkpoints/stage_a_v1",
    )
    stage_b = _write_stage_yaml(
        tmp_path / "b.yaml",
        step_function="super3_sample_level_step",
        checkpoint_save="/checkpoints/stage_b_v1",
    )
    fake = _RecordingFinetune()

    run_two_stage_finetune(
        stage_a, stage_b, finetune_fn=fake, recipe_builder=_fake_recipe_builder
    )

    stage_a_overrides = fake.calls[0]["cli_overrides"]
    assert not any(
        o.startswith("checkpoint.pretrained_checkpoint=")
        for o in stage_a_overrides
    )


def test_operator_cli_overrides_flow_into_both_stages(tmp_path: Path) -> None:
    """A run-level override (e.g., wandb tag) must reach BOTH stages,
    not just one."""
    stage_a = _write_stage_yaml(
        tmp_path / "a.yaml",
        step_function="gpt_step",
        checkpoint_save="/tmp/stage_a",
    )
    stage_b = _write_stage_yaml(
        tmp_path / "b.yaml",
        step_function="super3_sample_level_step",
        checkpoint_save="/tmp/stage_b",
    )
    fake = _RecordingFinetune()

    run_two_stage_finetune(
        stage_a,
        stage_b,
        finetune_fn=fake,
        recipe_builder=_fake_recipe_builder,
        cli_overrides=["logger.wandb_exp_name=eval_run_42"],
    )

    for call in fake.calls:
        assert "logger.wandb_exp_name=eval_run_42" in call["cli_overrides"]


def test_driver_tags_stage_invocations_for_telemetry(tmp_path: Path) -> None:
    """Tags ride into W&B run tags so downstream dashboards can split
    Stage A vs Stage B without inspecting config paths."""
    stage_a = _write_stage_yaml(
        tmp_path / "a.yaml",
        step_function="gpt_step",
        checkpoint_save="/tmp/stage_a",
    )
    stage_b = _write_stage_yaml(
        tmp_path / "b.yaml",
        step_function="super3_sample_level_step",
        checkpoint_save="/tmp/stage_b",
    )
    fake = _RecordingFinetune()

    run_two_stage_finetune(
        stage_a, stage_b, finetune_fn=fake, recipe_builder=_fake_recipe_builder
    )

    assert "stage-a" in fake.calls[0]["tags"]
    assert "token-level" in fake.calls[0]["tags"]
    assert "stage-b" in fake.calls[1]["tags"]
    assert "sample-level" in fake.calls[1]["tags"]
    # task013 tag on both for easy filter
    assert "task013" in fake.calls[0]["tags"]
    assert "task013" in fake.calls[1]["tags"]


def test_result_captures_both_checkpoint_save_paths(tmp_path: Path) -> None:
    stage_a = _write_stage_yaml(
        tmp_path / "a.yaml",
        step_function="gpt_step",
        checkpoint_save="/checkpoints/stage_a_v3",
    )
    stage_b = _write_stage_yaml(
        tmp_path / "b.yaml",
        step_function="super3_sample_level_step",
        checkpoint_save="/checkpoints/stage_b_v3",
    )
    fake = _RecordingFinetune()

    result = run_two_stage_finetune(
        stage_a, stage_b, finetune_fn=fake, recipe_builder=_fake_recipe_builder
    )

    assert result.stage_a_checkpoint_save == "/checkpoints/stage_a_v3"
    assert result.stage_b_checkpoint_save == "/checkpoints/stage_b_v3"
    assert len(result.invocations) == 2
    assert all(isinstance(inv, StageInvocation) for inv in result.invocations)
    assert result.invocations[0].stage == "a"
    assert result.invocations[1].stage == "b"


# ---------- step_function validation ----------


def test_driver_rejects_stage_a_using_sample_level_step(tmp_path: Path) -> None:
    """Stage A MUST be token-level (gpt_step). If a config drift sets
    Stage A to sample-level, the driver catches it before training
    runs — failing fast saves cluster time."""
    stage_a = _write_stage_yaml(
        tmp_path / "a.yaml",
        step_function="super3_sample_level_step",  # wrong
        checkpoint_save="/tmp/stage_a",
    )
    stage_b = _write_stage_yaml(
        tmp_path / "b.yaml",
        step_function="super3_sample_level_step",
        checkpoint_save="/tmp/stage_b",
    )
    fake = _RecordingFinetune()

    with pytest.raises(ValueError, match="Stage A.*gpt_step"):
        run_two_stage_finetune(
            stage_a, stage_b, finetune_fn=fake, recipe_builder=_fake_recipe_builder
        )
    # No invocations should have happened
    assert fake.calls == []


def test_driver_rejects_stage_b_using_gpt_step(tmp_path: Path) -> None:
    stage_a = _write_stage_yaml(
        tmp_path / "a.yaml",
        step_function="gpt_step",
        checkpoint_save="/tmp/stage_a",
    )
    stage_b = _write_stage_yaml(
        tmp_path / "b.yaml",
        step_function="gpt_step",  # wrong — Stage B must be sample-level
        checkpoint_save="/tmp/stage_b",
    )
    fake = _RecordingFinetune()

    with pytest.raises(ValueError, match="Stage B.*super3_sample_level_step"):
        run_two_stage_finetune(
            stage_a, stage_b, finetune_fn=fake, recipe_builder=_fake_recipe_builder
        )
    assert fake.calls == []


def test_driver_accepts_stage_a_without_explicit_step_function(tmp_path: Path) -> None:
    """If Stage A YAML omits ``step_function``, that defaults to
    gpt_step — same fall-back behavior as ``train.run_finetune``."""
    stage_a_path = tmp_path / "a.yaml"
    stage_a_path.write_text(
        yaml.safe_dump({"checkpoint": {"save": "/tmp/stage_a"}}),
        encoding="utf-8",
    )
    stage_b = _write_stage_yaml(
        tmp_path / "b.yaml",
        step_function="super3_sample_level_step",
        checkpoint_save="/tmp/stage_b",
    )
    fake = _RecordingFinetune()

    run_two_stage_finetune(
        stage_a_path, stage_b, finetune_fn=fake, recipe_builder=_fake_recipe_builder
    )
    assert len(fake.calls) == 2  # Stage A inferred as gpt_step → dispatch went through


# ---------- File / shape error surfaces ----------


def test_driver_raises_when_stage_a_yaml_missing(tmp_path: Path) -> None:
    stage_b = _write_stage_yaml(
        tmp_path / "b.yaml",
        step_function="super3_sample_level_step",
        checkpoint_save="/tmp/stage_b",
    )
    fake = _RecordingFinetune()
    with pytest.raises(FileNotFoundError, match="two-stage config"):
        run_two_stage_finetune(
            tmp_path / "nonexistent_a.yaml",
            stage_b,
            finetune_fn=fake,
            recipe_builder=_fake_recipe_builder,
        )


def test_driver_raises_when_checkpoint_save_missing(tmp_path: Path) -> None:
    """The whole point of the driver is to thread Stage A's
    ``checkpoint.save`` into Stage B; without it, the chain breaks."""
    stage_a = tmp_path / "a.yaml"
    stage_a.write_text(
        yaml.safe_dump({"step_function": "gpt_step", "checkpoint": {}}),
        encoding="utf-8",
    )
    stage_b = _write_stage_yaml(
        tmp_path / "b.yaml",
        step_function="super3_sample_level_step",
        checkpoint_save="/tmp/stage_b",
    )
    fake = _RecordingFinetune()
    with pytest.raises(ValueError, match="checkpoint.save"):
        run_two_stage_finetune(
            stage_a, stage_b, finetune_fn=fake, recipe_builder=_fake_recipe_builder
        )


# ---------- Shipped default configs ----------


def test_shipped_stage_a_default_satisfies_driver_preconditions() -> None:
    """The shipped ``stage_a_default.yaml`` must pass driver validation:
    step_function resolves to gpt_step and checkpoint.save is set."""
    data = yaml.safe_load(STAGE_A_DEFAULT_PATH.read_text(encoding="utf-8"))
    # step_function set explicitly to gpt_step in the shipped config
    assert data["step_function"] == "gpt_step"
    # checkpoint.save is a real path
    save_path = data["checkpoint"]["save"]
    assert isinstance(save_path, str) and save_path.strip()
    # Stage A and Stage B paths must differ so Stage B doesn't overwrite
    # Stage A mid-run
    stage_b = yaml.safe_load(STAGE_B_DEFAULT_PATH.read_text(encoding="utf-8"))
    assert save_path != stage_b["checkpoint"]["save"]


def test_shipped_stage_b_default_uses_sample_level_step() -> None:
    data = yaml.safe_load(STAGE_B_DEFAULT_PATH.read_text(encoding="utf-8"))
    assert data["step_function"] == "super3_sample_level_step"
    save_path = data["checkpoint"]["save"]
    assert isinstance(save_path, str) and save_path.strip()
    # The pretrained_checkpoint field must be present (driver overrides
    # it via CLI) so the YAML is self-documenting about the dependency
    assert "pretrained_checkpoint" in data["checkpoint"]


def test_shipped_defaults_drive_a_clean_two_stage_run() -> None:
    """End-to-end smoke against the shipped configs — driver loads
    both, validates step_function on each side, dispatches twice with
    the right overrides."""
    fake = _RecordingFinetune()
    result = run_two_stage_finetune(
        STAGE_A_DEFAULT_PATH,
        STAGE_B_DEFAULT_PATH,
        finetune_fn=fake,
        recipe_builder=_fake_recipe_builder,
    )
    assert len(fake.calls) == 2
    # Stage B overrides reference Stage A's actual save path from the
    # shipped YAML — the cross-walk is real, not synthetic.
    stage_a_data = yaml.safe_load(STAGE_A_DEFAULT_PATH.read_text(encoding="utf-8"))
    stage_a_save = stage_a_data["checkpoint"]["save"]
    stage_b_overrides = fake.calls[1]["cli_overrides"]
    assert any(
        o == f"checkpoint.pretrained_checkpoint={stage_a_save}"
        for o in stage_b_overrides
    )
    assert result.stage_a_checkpoint_save == stage_a_save
