"""Lightweight cross-stage lineage records (task021 Session 2).

`environment_registry.yaml` already declares per-env reward / verifier
contracts. This module adds the orthogonal *cross-stage* contract: every
M0 / M1 / RL / eval stage emits a `lineage` block inside its
`manifest.json` so downstream stages can find their upstream artifact,
walk back to the raw HF sources, and reason about freshness without
having to introspect each prep script.

Design notes:

- Dataclasses only — no pydantic. This module sits inside the data-prep
  scripts that already need to be runnable without the full
  ``nemotron.kit`` artifact / W&B stack. ``Artifact`` in
  ``nemotron.kit.artifacts.base`` is heavier and stays for the W&B
  publish path (task021 Session 3+).
- JSON-roundtrippable. ``LineageRecord.to_jsonable`` and
  ``LineageRecord.from_jsonable`` are the on-disk contract; everything
  else is convenience.
- Artifact-type names align with plan §10 lineage vocabulary
  (``RawDataArtifact → SFTDataArtifact → ModelArtifact-sft → ...``).
  When task021 Session 3 wires W&B publishing, the lineage block becomes
  the source of truth for the W&B artifact graph.

Walker semantics: a record's ``inputs`` list can contain entries with
``kind="manifest"`` whose ``ref`` is a filesystem path (absolute, or
relative to the current manifest's directory). ``walk_chain`` follows
those edges and returns the chain oldest → newest. Missing files are
skipped silently so a partially-realized chain stays inspectable.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

JsonDict = dict[str, Any]

LINEAGE_SCHEMA_VERSION = 1

# Plan §10 artifact-type vocabulary. Each stage emits a record claiming
# one of these names; downstream stages declare the upstream record as a
# `manifest`-kind input to keep the chain walkable.
RAW_DATA_ARTIFACT = "RawDataArtifact"      # M0 NeMo-Gym JSONL output
SFT_DATA_ARTIFACT = "SFTDataArtifact"      # M1 OpenAI chat JSONL output
PACKED_SFT_ARTIFACT = "PackedSFTArtifact"  # Xenna packed parquet shards (future)
MODEL_ARTIFACT_SFT = "ModelArtifact-sft"   # SFT checkpoint (future)
RLVR1_ARTIFACT = "RLVR1"                   # RLVR stage 1 (future)
RLVR2_ARTIFACT = "RLVR2"                   # RLVR stage 2 (future)
RLVR3_ARTIFACT = "RLVR3"                   # RLVR stage 3 (future)
SWE1_ARTIFACT = "SWE1"                     # SWE pivot (future)
SWE2_ARTIFACT = "SWE2"                     # SWE-Bench OpenHands (future)
RLHF_ARTIFACT = "RLHF"                     # Final RLHF (future)
EVAL_REPORT_ARTIFACT = "EvalReport"        # Benchmark report (future)

KNOWN_ARTIFACT_TYPES = frozenset(
    {
        RAW_DATA_ARTIFACT,
        SFT_DATA_ARTIFACT,
        PACKED_SFT_ARTIFACT,
        MODEL_ARTIFACT_SFT,
        RLVR1_ARTIFACT,
        RLVR2_ARTIFACT,
        RLVR3_ARTIFACT,
        SWE1_ARTIFACT,
        SWE2_ARTIFACT,
        RLHF_ARTIFACT,
        EVAL_REPORT_ARTIFACT,
    }
)


def now_utc_iso() -> str:
    """ISO-8601 UTC timestamp (second precision)."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class LineageInput:
    """A reference to something this stage consumed.

    `kind` is open-vocabulary but the established ones are:

    - ``"hf_dataset"`` — an upstream HF source (with optional config /
      split / revision).
    - ``"manifest"`` — points at another manifest.json so the walker can
      recurse. `ref` is a filesystem path (absolute, or relative to the
      manifest that declares this input).
    - ``"checkpoint"`` — a pretrained / SFT / RL checkpoint directory.
    """

    kind: str
    ref: str
    revision: str | None = None
    config: str | None = None
    split: str | None = None
    rows: int | None = None
    sha256: str | None = None
    notes: str | None = None


@dataclass
class LineageOutput:
    """A reference to something this stage produced.

    `ref` is the relative path under the producing manifest's directory
    by convention, so the manifest is self-contained.
    """

    kind: str
    ref: str
    rows: int | None = None
    sha256: str | None = None
    notes: str | None = None


@dataclass
class LineageRecord:
    """Top-level lineage block emitted by a prep / training stage.

    Lives at ``manifest["lineage"]`` in each stage's manifest.json.
    """

    schema_version: int
    stage: str           # plan §3 stage name ("M0 data_env_foundation", etc.)
    produced_by: str     # script filename or module path
    produced_at_utc: str
    artifact_type: str   # one of KNOWN_ARTIFACT_TYPES (warned-on otherwise)
    artifact_name: str   # human-readable id (eg. "m0_data_env_foundation-smoke-20260516")
    inputs: list[LineageInput] = field(default_factory=list)
    outputs: list[LineageOutput] = field(default_factory=list)

    def to_jsonable(self) -> JsonDict:
        return {
            "schema_version": self.schema_version,
            "stage": self.stage,
            "produced_by": self.produced_by,
            "produced_at_utc": self.produced_at_utc,
            "artifact_type": self.artifact_type,
            "artifact_name": self.artifact_name,
            "inputs": [_strip_none(asdict(inp)) for inp in self.inputs],
            "outputs": [_strip_none(asdict(out)) for out in self.outputs],
        }

    @classmethod
    def from_jsonable(cls, data: Mapping[str, Any]) -> LineageRecord:
        return cls(
            schema_version=int(data["schema_version"]),
            stage=str(data["stage"]),
            produced_by=str(data["produced_by"]),
            produced_at_utc=str(data["produced_at_utc"]),
            artifact_type=str(data["artifact_type"]),
            artifact_name=str(data["artifact_name"]),
            inputs=[LineageInput(**inp) for inp in (data.get("inputs") or [])],
            outputs=[LineageOutput(**out) for out in (data.get("outputs") or [])],
        )


def _strip_none(d: Mapping[str, Any]) -> JsonDict:
    """Drop keys with None values so the on-disk JSON stays tight."""
    return {k: v for k, v in d.items() if v is not None}


def make_record(
    *,
    stage: str,
    produced_by: str,
    artifact_type: str,
    artifact_name: str,
    inputs: Iterable[LineageInput] = (),
    outputs: Iterable[LineageOutput] = (),
) -> LineageRecord:
    """Build a LineageRecord with the current UTC timestamp and the pinned
    schema version. Callers pass already-shaped inputs/outputs."""
    return LineageRecord(
        schema_version=LINEAGE_SCHEMA_VERSION,
        stage=stage,
        produced_by=produced_by,
        produced_at_utc=now_utc_iso(),
        artifact_type=artifact_type,
        artifact_name=artifact_name,
        inputs=list(inputs),
        outputs=list(outputs),
    )


def _walk_chain_with_paths(starting_manifest: Path) -> list[tuple[Path, LineageRecord]]:
    """Walk a lineage chain, preserving each record's declaring manifest path."""
    chain: list[tuple[Path, LineageRecord]] = []
    visited: set[Path] = set()

    def _walk(path: Path) -> None:
        try:
            resolved = path.resolve(strict=False)
        except OSError:
            return
        if resolved in visited:
            return
        visited.add(resolved)
        try:
            with resolved.open(encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return
        lineage_data = data.get("lineage") if isinstance(data, Mapping) else None
        if not isinstance(lineage_data, Mapping):
            return
        record = LineageRecord.from_jsonable(lineage_data)
        # Recurse on manifest-kind inputs first so chain ends up
        # oldest-first when appended.
        for inp in record.inputs:
            if inp.kind != "manifest":
                continue
            upstream = Path(inp.ref)
            if not upstream.is_absolute():
                upstream = resolved.parent / upstream
            _walk(upstream)
        chain.append((resolved, record))

    _walk(starting_manifest)
    return chain


def walk_chain(starting_manifest: Path) -> list[LineageRecord]:
    """Walk the lineage chain back from a starting manifest.

    Returns records ordered oldest → newest. Missing / unreadable manifest
    files are silently skipped; this lets a partially-realized chain stay
    inspectable while still flagging broken edges via `validate_chain`.
    """
    return [record for _, record in _walk_chain_with_paths(starting_manifest)]


def _resolve_manifest_input_ref(declaring_manifest: Path, ref: str) -> Path:
    ref_path = Path(ref)
    if ref_path.is_absolute():
        return ref_path
    return declaring_manifest.parent / ref_path


def validate_chain(starting_manifest: Path) -> list[str]:
    """Return human-readable issues with the lineage chain. Empty = clean.

    Checks:
    - the starting manifest carries a lineage block at all
    - every non-root record declares at least one `manifest`-kind input
    - every `manifest`-kind input resolves to a file that exists on disk
    - declared `artifact_type` is in `KNOWN_ARTIFACT_TYPES` (warning, not
      a hard error — the vocabulary is plan-§10 aligned but extensible)
    """
    issues: list[str] = []
    if not starting_manifest.exists():
        return [f"starting manifest {starting_manifest} does not exist"]

    chain = _walk_chain_with_paths(starting_manifest)
    if not chain:
        issues.append(
            f"no lineage records found starting from {starting_manifest} — "
            "manifest is missing `lineage` block or the chain is empty"
        )
        return issues

    visited_refs: set[Path] = set()
    for index, (declaring_manifest, record) in enumerate(chain):
        # `KNOWN_ARTIFACT_TYPES` is a soft check — emit a warning-style
        # note but don't gate on it.
        if record.artifact_type not in KNOWN_ARTIFACT_TYPES:
            issues.append(
                f"record {record.stage} ({record.artifact_type}) is not in plan §10 "
                "vocabulary — add to lineage.py KNOWN_ARTIFACT_TYPES or align the type name"
            )
        manifest_inputs = [inp for inp in record.inputs if inp.kind == "manifest"]
        # The oldest record (e.g. M0) is allowed to have no manifest
        # input — its inputs are typically `hf_dataset` and other roots.
        is_root = index == 0
        if not manifest_inputs and not is_root:
            issues.append(
                f"record {record.stage} ({record.artifact_type}) declares no "
                "`manifest` input — chain may be broken"
            )
        for inp in manifest_inputs:
            ref_path = _resolve_manifest_input_ref(declaring_manifest, inp.ref)
            try:
                resolved_ref = ref_path.resolve(strict=False)
            except OSError:
                resolved_ref = ref_path
            if not ref_path.is_file():
                if resolved_ref not in visited_refs:
                    issues.append(
                        f"record {record.stage} input `manifest` ref {inp.ref} "
                        f"declared in {declaring_manifest} did not resolve to "
                        f"an existing file ({resolved_ref})"
                    )
                    visited_refs.add(resolved_ref)

    return issues
