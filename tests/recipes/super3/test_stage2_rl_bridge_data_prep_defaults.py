"""Stage2 RL data-prep defaults must consume bridge combined JSONL outputs."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from nemotron.data_prep.recipes import rl_local
from nemotron.data_prep.recipes.rl_local import run_resolve_and_split, split_local_jsonl
from nemotron.kit.train_script import resolve_repo_relative_source_path
from nemotron.recipes.super3.stage2_rl.data_prep import RLDataPrepConfig

yaml = pytest.importorskip("yaml")
OmegaConf = pytest.importorskip("omegaconf").OmegaConf


REPO_ROOT = Path(__file__).resolve().parents[3]
STAGE2_RL_ROOT = REPO_ROOT / "src/nemotron/recipes/super3/stage2_rl"
GENERIC_DEFAULT_CONFIG = STAGE2_RL_ROOT / "config/data_prep/default.yaml"
TINY_CONFIG = STAGE2_RL_ROOT / "config/data_prep/tiny.yaml"

DEFAULTS = {
    "swe1": STAGE2_RL_ROOT / "stage2_swe1/config/data_prep/default.yaml",
    "swe2": STAGE2_RL_ROOT / "stage2_swe2/config/data_prep/default.yaml",
    "rlhf": STAGE2_RL_ROOT / "stage3_rlhf/config/data_prep/default.yaml",
}

PROFILE_CONFIGS = {
    "tiny": TINY_CONFIG,
    "rlvr1": STAGE2_RL_ROOT / "stage1_rlvr/config/data_prep/rlvr1.yaml",
    "rlvr2": STAGE2_RL_ROOT / "stage1_rlvr/config/data_prep/rlvr2.yaml",
    "rlvr3": STAGE2_RL_ROOT / "stage1_rlvr/config/data_prep/rlvr3.yaml",
    **DEFAULTS,
}

EXPECTED_PROFILE_OUTPUT_SUFFIXES = {
    "tiny": Path("output/super3/stage2_rl_tiny"),
    "rlvr1": Path("output/super3/stage2_rl/rlvr1"),
    "rlvr2": Path("output/super3/stage2_rl/rlvr2"),
    "rlvr3": Path("output/super3/stage2_rl/rlvr3"),
    "swe1": Path("output/super3/stage2_rl/swe1"),
    "swe2": Path("output/super3/stage2_rl/swe2"),
    "rlhf": Path("output/super3/stage2_rl/rlhf"),
}

EXPECTED_PROFILE_OUTPUT_DIRS = {
    profile: f"${{oc.env:NEMO_RUN_DIR,.}}/{suffix.as_posix()}"
    for profile, suffix in EXPECTED_PROFILE_OUTPUT_SUFFIXES.items()
}

EXPECTED_BRIDGE_INPUT_PATHS = {
    "rlvr1": "${oc.env:NEMO_RUN_DIR,.}/output/super3/m1_rlvr/rlvr1/combined.jsonl",
    "rlvr2": "${oc.env:NEMO_RUN_DIR,.}/output/super3/m1_rlvr/rlvr2/combined.jsonl",
    "rlvr3": "${oc.env:NEMO_RUN_DIR,.}/output/super3/m1_rlvr/rlvr3/combined.jsonl",
    "swe1": "${oc.env:NEMO_RUN_DIR,.}/output/super3/m1_swe1/combined.jsonl",
    "swe2": "${oc.env:NEMO_RUN_DIR,.}/output/super3/m1_swe2/combined.jsonl",
    "rlhf": "${oc.env:NEMO_RUN_DIR,.}/output/super3/m1_rlhf/combined.jsonl",
}

CORE_BLEND_CONFIGS = {
    "default": GENERIC_DEFAULT_CONFIG,
    "tiny": TINY_CONFIG,
}

EXPECTED_CORE_BLEND_PATH = (
    "src/nemotron/recipes/super3/stage2_rl/config/data_prep/data_blend_raw.json"
)


def _load_yaml(path: Path) -> tuple[str, dict[str, object]]:
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    assert isinstance(data, dict), f"{path}: top-level YAML must be a mapping"
    return text, data


@pytest.mark.parametrize("profile", sorted(CORE_BLEND_CONFIGS))
def test_stage2_rl_core_blend_paths_are_repo_local(profile: str) -> None:
    text, data = _load_yaml(CORE_BLEND_CONFIGS[profile])

    assert data["blend_path"] == EXPECTED_CORE_BLEND_PATH
    assert "${oc.env:PWD}/src/" not in text


@pytest.mark.parametrize("profile", sorted(CORE_BLEND_CONFIGS))
def test_stage2_rl_core_blend_paths_resolve_from_non_repo_cwd(
    profile: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_path = CORE_BLEND_CONFIGS[profile]
    monkeypatch.chdir(tmp_path)
    _, data = _load_yaml(config_path)

    blend_path = resolve_repo_relative_source_path(
        data["blend_path"],
        anchor_file=config_path,
    )

    assert blend_path == REPO_ROOT / EXPECTED_CORE_BLEND_PATH
    assert blend_path.is_file()


def test_stage2_rl_config_dataclass_resolves_repo_local_blend_path() -> None:
    cfg = RLDataPrepConfig(blend_path=EXPECTED_CORE_BLEND_PATH)

    assert cfg.blend_path == REPO_ROOT / EXPECTED_CORE_BLEND_PATH


def test_stage2_rl_config_dataclass_preserves_relative_override() -> None:
    cfg = RLDataPrepConfig(blend_path="custom/blend.json")

    assert cfg.blend_path == Path("custom/blend.json")


@pytest.mark.parametrize("profile", sorted(PROFILE_CONFIGS))
def test_stage2_rl_data_prep_profile_output_dirs_are_portable(profile: str) -> None:
    text, data = _load_yaml(PROFILE_CONFIGS[profile])

    assert "/../output/super3/" not in text
    assert data["output_dir"] == EXPECTED_PROFILE_OUTPUT_DIRS[profile]
    assert "${oc.env:PWD}" not in data["output_dir"]
    assert data["output_dir"].startswith("${oc.env:NEMO_RUN_DIR,.}/output/super3/")


@pytest.mark.parametrize("profile", sorted(PROFILE_CONFIGS))
def test_stage2_rl_data_prep_profile_output_dirs_resolve_under_run_dir(
    profile: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("NEMO_RUN_DIR", str(tmp_path))

    cfg = OmegaConf.load(PROFILE_CONFIGS[profile])
    output_dir = Path(cfg.output_dir)

    assert output_dir == tmp_path / EXPECTED_PROFILE_OUTPUT_SUFFIXES[profile]
    assert output_dir.is_relative_to(tmp_path / "output" / "super3")


@pytest.mark.parametrize("profile", sorted(EXPECTED_BRIDGE_INPUT_PATHS))
def test_stage2_rl_bridge_profiles_keep_input_and_auto_holdout(profile: str) -> None:
    _, data = _load_yaml(PROFILE_CONFIGS[profile])

    assert data["input_path"] == EXPECTED_BRIDGE_INPUT_PATHS[profile]
    assert data["val_holdout"] == "auto"


def test_stage2_rl_data_prep_output_dirs_do_not_use_pwd_template() -> None:
    offenders = []
    for path in STAGE2_RL_ROOT.rglob("config/data_prep/*.yaml"):
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("output_dir:") and "${oc.env:PWD}" in stripped:
                offenders.append(f"{path.relative_to(REPO_ROOT)}:{line_no}:{stripped}")

    assert offenders == []


@pytest.mark.parametrize(("mix", "config_path"), DEFAULTS.items())
def test_stage2_rl_default_input_path_uses_bridge_combined_jsonl(
    mix: str, config_path: Path
) -> None:
    text = config_path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)

    assert "/lustre/" not in text
    assert "yifuw" not in text
    assert "combined.jsonl" in data["input_path"]
    assert "${oc.env:NEMO_RUN_DIR" in data["input_path"]
    assert f"m1_{mix}/combined.jsonl" in data["input_path"]


@pytest.mark.parametrize(("mix", "config_path"), DEFAULTS.items())
def test_stage2_rl_default_preserves_data_prep_config_fields(
    mix: str, config_path: Path
) -> None:
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    for field in ("input_path", "output_dir", "val_holdout", "sample", "force"):
        assert field in data, f"{mix} data_prep default missing field {field}"

    assert data["val_holdout"] == "auto"


def test_generic_stage2_rl_default_output_dir_is_nemo_run_dir_portable() -> None:
    text = GENERIC_DEFAULT_CONFIG.read_text(encoding="utf-8")
    data = yaml.safe_load(text)

    assert data["output_dir"] == "${oc.env:NEMO_RUN_DIR,.}/output/super3/stage2_rl_resolved"
    assert "${oc.env:PWD}" not in data["output_dir"]
    assert "/../output/stage2_rl_resolved" not in data["output_dir"]


def test_generic_stage2_rl_default_output_dir_matches_dataclass_default() -> None:
    cfg = OmegaConf.load(GENERIC_DEFAULT_CONFIG)

    assert Path(cfg.output_dir) == RLDataPrepConfig().output_dir
    assert Path(cfg.output_dir).as_posix().endswith("output/super3/stage2_rl_resolved")


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rewrite_same_size_same_mtime(path: Path, text: str) -> None:
    stat = path.stat()
    assert len(text.encode("utf-8")) == stat.st_size
    path.write_text(text, encoding="utf-8")
    os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    after = path.stat()
    assert after.st_size == stat.st_size
    assert after.st_mtime_ns == stat.st_mtime_ns


def test_split_local_jsonl_infers_bridge_holdout_from_manifest_counts(tmp_path: Path) -> None:
    bridge_dir = tmp_path / "m1_swe1"
    bridge_dir.mkdir()
    combined_path = bridge_dir / "combined.jsonl"
    train_rows = [{"id": f"train-{i}", "split": "train"} for i in range(7)]
    val_rows = [{"id": f"val-{i}", "split": "val"} for i in range(3)]
    _write_jsonl(combined_path, [*train_rows, *val_rows])
    (bridge_dir / "manifest.json").write_text(
        json.dumps(
            {
                "counts": {
                    "train": {"swe_pivot_demo": len(train_rows)},
                    "val": {"swe_pivot_demo": len(val_rows)},
                }
            }
        ),
        encoding="utf-8",
    )

    result = split_local_jsonl(
        input_path=combined_path,
        output_dir=tmp_path / "stage2_out",
        val_holdout="auto",
        force=True,
    )

    assert result.train_rows == len(train_rows)
    assert result.val_rows == len(val_rows)
    assert _read_jsonl(Path(result.train_path)) == train_rows
    assert result.val_path is not None
    assert _read_jsonl(Path(result.val_path)) == val_rows

    manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
    assert manifest["val_holdout"] == len(val_rows)
    assert manifest["val_holdout_source"] == "bridge_manifest"
    assert manifest["bridge_manifest"]["val_rows"] == len(val_rows)
    assert manifest["input_sha256"] == _sha256(combined_path)
    assert manifest["bridge_manifest"]["sha256"] == _sha256(bridge_dir / "manifest.json")


def test_split_local_jsonl_cache_invalidates_on_same_stat_content_change(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "plain.jsonl"
    rows_a = [{"id": f"A{i}", "split": "train"} for i in range(4)]
    rows_b = [{"id": f"B{i}", "split": "train"} for i in range(4)]
    _write_jsonl(input_path, rows_a)

    result_a = split_local_jsonl(
        input_path=input_path,
        output_dir=tmp_path / "out",
        val_holdout=1,
        force=False,
    )
    manifest_a = json.loads(Path(result_a.manifest_path).read_text(encoding="utf-8"))

    _rewrite_same_size_same_mtime(
        input_path,
        "".join(json.dumps(row) + "\n" for row in rows_b),
    )
    result_b = split_local_jsonl(
        input_path=input_path,
        output_dir=tmp_path / "out",
        val_holdout=1,
        force=False,
    )
    manifest_b = json.loads(Path(result_b.manifest_path).read_text(encoding="utf-8"))

    assert manifest_a["run_hash"] != manifest_b["run_hash"]
    assert manifest_a["input_sha256"] != manifest_b["input_sha256"]
    assert manifest_b["input_sha256"] == _sha256(input_path)
    assert _read_jsonl(Path(result_b.train_path)) == rows_b[:-1]


def test_split_local_jsonl_auto_holdout_cache_includes_bridge_manifest_content(
    tmp_path: Path,
) -> None:
    bridge_dir = tmp_path / "m1_swe2"
    bridge_dir.mkdir()
    combined_path = bridge_dir / "combined.jsonl"
    rows = [{"id": f"row-{i}"} for i in range(5)]
    _write_jsonl(combined_path, rows)
    manifest_path = bridge_dir / "manifest.json"
    manifest_a = {
        "counts": {"train": {"swe2": 3}, "val": {"swe2": 2}},
        "lineage_marker": "AAAA",
    }
    manifest_b = {
        "counts": {"train": {"swe2": 3}, "val": {"swe2": 2}},
        "lineage_marker": "BBBB",
    }
    manifest_path.write_text(json.dumps(manifest_a, sort_keys=True), encoding="utf-8")

    result_a = split_local_jsonl(
        input_path=combined_path,
        output_dir=tmp_path / "out",
        val_holdout="auto",
        force=False,
    )
    output_manifest_a = json.loads(Path(result_a.manifest_path).read_text(encoding="utf-8"))

    _rewrite_same_size_same_mtime(
        manifest_path,
        json.dumps(manifest_b, sort_keys=True),
    )
    result_b = split_local_jsonl(
        input_path=combined_path,
        output_dir=tmp_path / "out",
        val_holdout="auto",
        force=False,
    )
    output_manifest_b = json.loads(Path(result_b.manifest_path).read_text(encoding="utf-8"))

    assert output_manifest_a["run_hash"] != output_manifest_b["run_hash"]
    assert output_manifest_a["bridge_manifest"]["sha256"] != output_manifest_b["bridge_manifest"]["sha256"]
    assert output_manifest_b["bridge_manifest"]["sha256"] == _sha256(manifest_path)


def test_split_local_jsonl_explicit_holdout_still_works_for_plain_jsonl(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "plain.jsonl"
    rows = [{"id": i} for i in range(8)]
    _write_jsonl(input_path, rows)

    result = split_local_jsonl(
        input_path=input_path,
        output_dir=tmp_path / "plain_out",
        val_holdout=2,
        force=True,
    )

    assert result.train_rows == 6
    assert result.val_rows == 2
    assert _read_jsonl(Path(result.train_path)) == rows[:6]
    assert result.val_path is not None
    assert _read_jsonl(Path(result.val_path)) == rows[-2:]


def test_split_local_jsonl_auto_holdout_requires_bridge_manifest(tmp_path: Path) -> None:
    combined_path = tmp_path / "combined.jsonl"
    _write_jsonl(combined_path, [{"id": i} for i in range(5)])

    with pytest.raises(FileNotFoundError, match="val_holdout=auto requires a bridge manifest"):
        split_local_jsonl(
            input_path=combined_path,
            output_dir=tmp_path / "out",
            val_holdout="auto",
            force=True,
        )


def test_split_local_jsonl_auto_holdout_rejects_bad_bridge_manifest_counts(
    tmp_path: Path,
) -> None:
    bridge_dir = tmp_path / "m1_rlhf"
    bridge_dir.mkdir()
    combined_path = bridge_dir / "combined.jsonl"
    _write_jsonl(combined_path, [{"id": i} for i in range(5)])
    (bridge_dir / "manifest.json").write_text(
        json.dumps({"counts": {"train": {"rlhf": 4}, "val": {"rlhf": 4}}}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Bridge manifest row count does not match combined JSONL"):
        split_local_jsonl(
            input_path=combined_path,
            output_dir=tmp_path / "out",
            val_holdout="auto",
            force=True,
        )


def _install_fake_resolve_pipeline(
    monkeypatch: pytest.MonkeyPatch,
    resolved_path: Path,
) -> None:
    def _fake_run_pipeline(_spec: object) -> None:
        return None

    def _fake_finalize_rl_run(*_args: object, **_kwargs: object) -> object:
        return SimpleNamespace(split_paths={"combined": str(resolved_path)})

    monkeypatch.setattr(rl_local.pipelines_v1, "run_pipeline", _fake_run_pipeline)
    monkeypatch.setattr(rl_local, "finalize_rl_run", _fake_finalize_rl_run)


def test_run_resolve_and_split_infers_auto_holdout_from_original_bridge_manifest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bridge_dir = tmp_path / "m1_rlvr" / "rlvr1"
    bridge_dir.mkdir(parents=True)
    combined_path = bridge_dir / "combined.jsonl"
    train_rows = [{"id": f"train-{i}", "split": "train"} for i in range(5)]
    val_rows = [{"id": f"val-{i}", "split": "val"} for i in range(4)]
    all_rows = [*train_rows, *val_rows]
    _write_jsonl(combined_path, all_rows)
    (bridge_dir / "manifest.json").write_text(
        json.dumps(
            {
                "counts": {
                    "train": {"rlvr1": len(train_rows)},
                    "val": {"rlvr1": len(val_rows)},
                }
            }
        ),
        encoding="utf-8",
    )
    resolved_dir = tmp_path / "resolved_without_manifest"
    resolved_dir.mkdir()
    resolved_path = resolved_dir / "resolved.jsonl"
    _write_jsonl(resolved_path, all_rows)
    _install_fake_resolve_pipeline(monkeypatch, resolved_path)

    result = run_resolve_and_split(
        input_path=combined_path,
        output_dir=tmp_path / "rlvr_out",
        val_holdout="auto",
        force=True,
        execution_mode="streaming",
    )

    assert result.train_rows == len(train_rows)
    assert result.val_rows == len(val_rows)
    assert _read_jsonl(Path(result.train_path)) == train_rows
    assert result.val_path is not None
    assert _read_jsonl(Path(result.val_path)) == val_rows
    manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
    assert manifest["val_holdout"] == len(val_rows)
    assert manifest["val_holdout_source"] == "bridge_manifest"
    assert manifest["bridge_manifest"]["path"].endswith("m1_rlvr/rlvr1/manifest.json")


def test_run_resolve_and_split_cache_identity_includes_source_content(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_path = tmp_path / "plain_rlvr.jsonl"
    rows_a = [{"id": f"A{i}", "split": "train"} for i in range(5)]
    rows_b = [{"id": f"B{i}", "split": "train"} for i in range(5)]
    _write_jsonl(input_path, rows_a)
    resolved_path = tmp_path / "resolved.jsonl"

    def _fake_run_pipeline(_spec: object) -> None:
        resolved_path.write_text(input_path.read_text(encoding="utf-8"), encoding="utf-8")

    def _fake_finalize_rl_run(*_args: object, **_kwargs: object) -> object:
        return SimpleNamespace(split_paths={"plain_rlvr": str(resolved_path)})

    monkeypatch.setattr(rl_local.pipelines_v1, "run_pipeline", _fake_run_pipeline)
    monkeypatch.setattr(rl_local, "finalize_rl_run", _fake_finalize_rl_run)

    result_a = run_resolve_and_split(
        input_path=input_path,
        output_dir=tmp_path / "plain_out",
        val_holdout=1,
        force=False,
        execution_mode="streaming",
    )
    manifest_a = json.loads(Path(result_a.manifest_path).read_text(encoding="utf-8"))

    _rewrite_same_size_same_mtime(
        input_path,
        "".join(json.dumps(row) + "\n" for row in rows_b),
    )
    result_b = run_resolve_and_split(
        input_path=input_path,
        output_dir=tmp_path / "plain_out",
        val_holdout=1,
        force=False,
        execution_mode="streaming",
    )
    manifest_b = json.loads(Path(result_b.manifest_path).read_text(encoding="utf-8"))

    resolve_config_hashes = {
        json.loads(config_path.read_text(encoding="utf-8"))["input_sha256"]
        for config_path in (tmp_path / "plain_out" / "resolved" / "runs").glob("*/config.json")
    }
    assert manifest_a["run_hash"] != manifest_b["run_hash"]
    assert manifest_a["input_sha256"] != manifest_b["input_sha256"]
    assert manifest_b["input_sha256"] == _sha256(resolved_path)
    assert _sha256(input_path) in resolve_config_hashes
    assert len(resolve_config_hashes) == 2
    assert _read_jsonl(Path(result_b.train_path)) == rows_b[:-1]


def test_run_resolve_and_split_preserves_explicit_numeric_holdout_for_plain_jsonl(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_path = tmp_path / "plain_rlvr.jsonl"
    rows = [{"id": i} for i in range(6)]
    _write_jsonl(input_path, rows)
    resolved_path = tmp_path / "resolved.jsonl"
    _write_jsonl(resolved_path, rows)
    _install_fake_resolve_pipeline(monkeypatch, resolved_path)

    result = run_resolve_and_split(
        input_path=input_path,
        output_dir=tmp_path / "plain_out",
        val_holdout=2,
        force=True,
        execution_mode="streaming",
    )

    assert result.train_rows == 4
    assert result.val_rows == 2
    assert _read_jsonl(Path(result.train_path)) == rows[:4]
    assert result.val_path is not None
    assert _read_jsonl(Path(result.val_path)) == rows[-2:]
