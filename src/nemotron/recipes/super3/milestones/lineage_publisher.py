# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""W&B artifact lineage publisher (task069 Session 1).

Plan §10 M1 infra explicitly lists:

> W&B/artifact lineage for raw data, prepared data, model checkpoints,
> and eval reports.

task021 Session 2 landed the lineage *schema* (`lineage.LineageRecord`
/ `LineageInput` / `LineageOutput` dataclasses + artifact-type
vocabulary as module constants). Today every M0 / M1 bridge writes a
``manifest.json`` with a lineage block — but those blocks are
local-only; nothing pushes them up to W&B where the operator's board
can render the chain.

This module is the runtime publish side: takes a `LineageRecord` plus
the directory where its outputs live, and emits the appropriate
`wandb.Artifact` calls. The W&B run object is *injectable* so:

- Sandbox tests use `FakeWandbRun` capturing `.log_artifact()` /
  `.use_artifact()` calls in a list for assertions
- Production callers pass the real `wandb.run` (or any object
  duck-compatible with it)
- Dry-run mode (no wandb_run provided) is a no-op — sandbox can import
  and call ``publish`` without raising

Pure stdlib; W&B never imported in this module (callers supply the run
object). Sandbox-runnable.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from nemotron.recipes.super3.milestones.lineage import (
    LineageInput,
    LineageOutput,
    LineageRecord,
)


# An upstream-artifact resolver takes a LineageInput and returns the
# W&B qualified name (``name:version`` or ``name:alias``) that the
# input points at, or None if the input doesn't have a corresponding
# W&B artifact (e.g., external HF datasets we don't ingest into W&B).
UpstreamResolver = Callable[[LineageInput], str | None]


def default_upstream_resolver(inp: LineageInput) -> str | None:
    """Default mapping from LineageInput → W&B qualified name.

    - ``manifest`` inputs: read the referenced manifest.json and read
      its lineage block's ``artifact_name``; return ``"<name>:latest"``.
      None if the upstream manifest can't be read (caller logs the gap).
    - ``hf_dataset`` inputs: None — external HF doesn't have a W&B
      artifact equivalent; the lineage record still records the
      reference, just not via `use_artifact`.
    - ``checkpoint`` inputs: ``"<basename>:latest"`` heuristic — the
      checkpoint's directory name is treated as the artifact name.
    - Other kinds: None.

    Operators with stricter naming conventions inject a custom resolver
    via ``WandbArtifactPublisher.publish(upstream_artifact_resolver=...)``.
    """
    if inp.kind == "manifest":
        manifest_path = Path(inp.ref)
        if not manifest_path.is_file():
            return None
        try:
            with manifest_path.open(encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return None
        lineage = data.get("lineage")
        if not isinstance(lineage, Mapping):
            return None
        upstream_name = lineage.get("artifact_name")
        if not isinstance(upstream_name, str) or not upstream_name.strip():
            return None
        return f"{upstream_name}:latest"
    if inp.kind == "checkpoint":
        return f"{Path(inp.ref).name}:latest"
    return None


@dataclass
class PublishResult:
    """Captured outcome of one ``publish`` call.

    Useful for both tests (assert on which artifacts got logged / used)
    and callers that want to log the publish step itself (a CLI prints
    this on stdout). ``dry_run`` is True when the publisher was
    constructed without a wandb_run.
    """

    dry_run: bool
    artifact_name: str | None
    artifact_type: str | None
    upstream_resolved: list[str] = field(default_factory=list)
    upstream_unresolved: list[str] = field(default_factory=list)
    outputs_attached: list[str] = field(default_factory=list)
    outputs_missing: list[str] = field(default_factory=list)


class WandbArtifactPublisher:
    """Publish a ``LineageRecord`` to W&B as artifact-lineage calls.

    Construction:

    - ``wandb_run`` is the W&B run object (``wandb.init()``'s return) or
      a fake. Passing ``None`` enables dry-run mode: ``publish`` is a
      no-op but still returns a ``PublishResult`` describing what would
      have been published (useful for CI / planning).
    - ``artifact_factory`` is a callable ``(name, type) -> Artifact``;
      defaults to importing ``wandb.Artifact`` lazily at publish time.
      Tests inject a fake factory so no real wandb import is needed.

    The publisher does NOT manage W&B run lifecycle — callers create the
    run, pass it in, and finish it.
    """

    def __init__(
        self,
        wandb_run: Any = None,
        *,
        artifact_factory: Callable[..., Any] | None = None,
    ) -> None:
        self.wandb_run = wandb_run
        self._artifact_factory = artifact_factory

    def publish(
        self,
        record: LineageRecord,
        *,
        file_root: Path | str | None = None,
        upstream_artifact_resolver: UpstreamResolver | None = None,
    ) -> PublishResult:
        """Translate *record* into W&B artifact lineage calls.

        *file_root* is the directory under which ``record.outputs[i].ref``
        is resolved. If None, output paths are taken as-is (suitable for
        absolute paths or when the caller doesn't care to attach files).

        *upstream_artifact_resolver* maps each input to a W&B qualified
        name; defaults to ``default_upstream_resolver``. Returning None
        for an input means "no W&B linkage" — the lineage block still
        records the reference, just not via ``use_artifact``.

        Dry-run mode: returns a ``PublishResult`` describing what WOULD
        have been published, without actually calling the W&B run.
        """
        resolver = upstream_artifact_resolver or default_upstream_resolver
        result = PublishResult(
            dry_run=self.wandb_run is None,
            artifact_name=record.artifact_name,
            artifact_type=record.artifact_type,
        )

        # Resolve every input first so the result reflects upstream
        # linkage decisions regardless of whether we're publishing.
        resolved_pairs: list[tuple[LineageInput, str]] = []
        for inp in record.inputs:
            resolved = resolver(inp)
            if resolved:
                result.upstream_resolved.append(resolved)
                resolved_pairs.append((inp, resolved))
            else:
                result.upstream_unresolved.append(f"{inp.kind}:{inp.ref}")

        # Walk outputs to plan file attachments; track missing files so
        # the caller knows when an artifact would be empty.
        root = Path(file_root) if file_root is not None else None
        output_attachments: list[Path] = []
        for out in record.outputs:
            target = Path(out.ref) if Path(out.ref).is_absolute() else (
                root / out.ref if root is not None else Path(out.ref)
            )
            if target.exists():
                result.outputs_attached.append(str(target))
                output_attachments.append(target)
            else:
                result.outputs_missing.append(str(target))

        if self.wandb_run is None:
            return result  # dry-run

        artifact = self._make_artifact(
            name=record.artifact_name, type=record.artifact_type
        )
        for path in output_attachments:
            artifact.add_file(str(path))

        for _, qualified_name in resolved_pairs:
            upstream = self.wandb_run.use_artifact(qualified_name)
            # Stash the upstream's kind in metadata so the W&B UI shows
            # the relationship type without re-reading the manifest.
            if hasattr(artifact, "metadata"):
                artifact.metadata["upstream_" + qualified_name.split(":")[0]] = (
                    qualified_name
                )
                # Touch upstream so static analyzers don't complain;
                # the use_artifact return is enough to register the edge.
                _ = upstream

        self.wandb_run.log_artifact(artifact)
        return result

    def _make_artifact(self, *, name: str, type: str) -> Any:
        """Build a `wandb.Artifact`-shaped object.

        Custom *artifact_factory* wins; otherwise lazy-import
        `wandb.Artifact`. Sandbox tests pass a fake factory so no real
        wandb import is needed.
        """
        if self._artifact_factory is not None:
            return self._artifact_factory(name=name, type=type)
        import wandb  # local import — caller's responsibility to have it

        return wandb.Artifact(name=name, type=type)


# ---------- Test doubles (sandbox-runnable; no wandb import needed) ----------


class FakeArtifact:
    """Captures `wandb.Artifact` lifecycle for tests.

    Records every ``add_file()`` call + every ``metadata`` mutation.
    Matches the parts of the wandb.Artifact surface the publisher
    touches; new surface uses go in here as the publisher grows.
    """

    def __init__(self, *, name: str, type: str) -> None:
        self.name = name
        self.type = type
        self.files: list[str] = []
        self.metadata: dict[str, Any] = {}

    def add_file(self, path: str) -> None:
        self.files.append(path)


class FakeWandbRun:
    """Captures `use_artifact` / `log_artifact` for tests.

    Two list fields make ordering assertions easy:

    - ``use_artifact_calls`` — qualified names passed in, in call order
    - ``log_artifact_calls`` — FakeArtifact instances logged, in call order
    """

    def __init__(self) -> None:
        self.use_artifact_calls: list[str] = []
        self.log_artifact_calls: list[FakeArtifact] = []

    def use_artifact(self, qualified_name: str) -> FakeArtifact:
        self.use_artifact_calls.append(qualified_name)
        # Return a placeholder; matches wandb.use_artifact contract.
        return FakeArtifact(name=qualified_name.split(":")[0], type="upstream")

    def log_artifact(self, artifact: FakeArtifact) -> None:
        self.log_artifact_calls.append(artifact)


__all__ = [
    "FakeArtifact",
    "FakeWandbRun",
    "PublishResult",
    "UpstreamResolver",
    "WandbArtifactPublisher",
    "default_upstream_resolver",
]
