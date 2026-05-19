# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""SWE2 sandbox watchdog policy + subprocess enforcer (task017 Session 2).

The SWE2 OpenHands loop runs untrusted agent-generated shell commands
inside a SIF container. The container itself (task021 / runtime_shim.py)
already imposes resource limits (CPU / memory) and image-level
isolation. This module adds the *policy* layer on top:

- ``command_blocklist`` — argv prefixes that must NEVER execute inside
  the sandbox (e.g. ``rm -rf /``, ``sudo``, ``curl http://external/``).
  Specifically protects against an LLM emitting a destructive command
  that *would* succeed inside the SIF if the sandbox-level limits don't
  catch it.
- ``network_policy`` — declarative intent for the egress firewall the
  cluster's SIF launcher should enforce. Values: ``deny`` (offline run),
  ``allow_internal`` (only NVIDIA-internal hostnames), ``allow`` (full
  egress, dev only). The Python layer doesn't *enforce* the network
  policy — that's the SIF launcher's job — but it records it as part of
  the policy contract so misalignment between policy and actual launch
  config is detectable.

Pure stdlib. ``enforce_subprocess`` wraps ``subprocess.run`` and raises
``SandboxPolicyViolation`` when the command would have been blocked.
Sandbox-runnable; real SIF integration is task021 / future cluster work.
"""

from __future__ import annotations

import shlex
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


VALID_NETWORK_POLICIES: frozenset[str] = frozenset({"deny", "allow_internal", "allow"})


@dataclass(frozen=True)
class WatchdogPolicy:
    """Sandbox security policy for the SWE2 OpenHands rollout.

    ``command_blocklist`` is a list of *argv prefixes*. A command is
    blocked iff its argv (split via shlex if a string) starts with any
    blocklisted prefix. Token-level prefix matching avoids substring
    false positives (a path ending in ``rm`` doesn't trip ``["rm"]``).

    ``network_policy`` is a declarative intent the runtime SIF launcher
    consumes; the Python layer records it for audit but doesn't enforce
    egress directly.

    Resource limits (``cpu_limit`` / ``memory_limit_mb``) duplicate
    ``runtime_shim.ContainerSandbox`` fields at the policy layer so the
    SIF launcher can cross-check policy vs container args at start time.
    """

    command_blocklist: tuple[tuple[str, ...], ...] = ()
    network_policy: str = "deny"
    cpu_limit: float | None = None
    memory_limit_mb: int | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)


class SandboxPolicyViolation(RuntimeError):
    """Raised when a subprocess call would violate the watchdog policy."""


def _coerce_blocklist(entries: Any) -> tuple[tuple[str, ...], ...]:
    """Normalise blocklist entries to ``tuple[tuple[str, ...], ...]``.

    Each entry can be a string (``"rm -rf /"`` — split via shlex) or a
    list of argv tokens (``["sudo", "-i"]`` — used as-is). Entries that
    don't parse to a non-empty list are dropped — the policy author can
    fix the YAML rather than triggering a crash on a typo.
    """
    if entries is None:
        return ()
    out: list[tuple[str, ...]] = []
    for entry in entries:
        if isinstance(entry, str):
            tokens = tuple(shlex.split(entry))
        elif isinstance(entry, Sequence) and not isinstance(entry, (str, bytes)):
            tokens = tuple(str(t) for t in entry if str(t))
        else:
            continue
        if tokens:
            out.append(tokens)
    return tuple(out)


def load_watchdog_policy(path: Path | str) -> WatchdogPolicy:
    """Read a watchdog policy YAML.

    Required field: ``network_policy`` (must be one of
    ``VALID_NETWORK_POLICIES``). Optional: ``command_blocklist`` /
    ``cpu_limit`` / ``memory_limit_mb`` / ``notes``. Unknown top-level
    keys are silently ignored so the YAML can carry author comments /
    metadata without crashing the loader.
    """
    import yaml  # local import — caller may not need yaml otherwise

    target = Path(path)
    raw = yaml.safe_load(target.read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise ValueError(f"{target}: watchdog policy must be a YAML mapping")

    network_policy = str(raw.get("network_policy", "")).strip()
    if network_policy not in VALID_NETWORK_POLICIES:
        raise ValueError(
            f"{target}: network_policy must be one of "
            f"{sorted(VALID_NETWORK_POLICIES)}, got {network_policy!r}"
        )

    blocklist_raw = raw.get("command_blocklist")
    if blocklist_raw is not None and not isinstance(blocklist_raw, list):
        raise ValueError(
            f"{target}: command_blocklist must be a list, got {type(blocklist_raw).__name__}"
        )
    blocklist = _coerce_blocklist(blocklist_raw)

    cpu_limit_raw = raw.get("cpu_limit")
    if cpu_limit_raw is None:
        cpu_limit: float | None = None
    else:
        try:
            cpu_limit = float(cpu_limit_raw)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{target}: cpu_limit must be numeric") from exc
        if cpu_limit <= 0:
            raise ValueError(f"{target}: cpu_limit must be > 0, got {cpu_limit}")

    memory_limit_raw = raw.get("memory_limit_mb")
    if memory_limit_raw is None:
        memory_limit_mb: int | None = None
    else:
        try:
            memory_limit_mb = int(memory_limit_raw)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{target}: memory_limit_mb must be integer") from exc
        if memory_limit_mb <= 0:
            raise ValueError(
                f"{target}: memory_limit_mb must be > 0, got {memory_limit_mb}"
            )

    notes_raw = raw.get("notes")
    if isinstance(notes_raw, list):
        notes = tuple(str(n) for n in notes_raw)
    elif isinstance(notes_raw, str):
        notes = (notes_raw,)
    else:
        notes = ()

    return WatchdogPolicy(
        command_blocklist=blocklist,
        network_policy=network_policy,
        cpu_limit=cpu_limit,
        memory_limit_mb=memory_limit_mb,
        notes=notes,
    )


def _split_argv(argv: str | Sequence[str]) -> tuple[str, ...]:
    if isinstance(argv, str):
        return tuple(shlex.split(argv))
    return tuple(str(token) for token in argv)


def is_command_blocked(policy: WatchdogPolicy, argv: str | Sequence[str]) -> bool:
    """Return True iff *argv* would be blocked by *policy*.

    Match rule: argv tokens start-with any blocklist entry token-for-token.
    Empty argv is treated as blocked (the runtime should reject empty
    commands anyway, but be explicit).
    """
    tokens = _split_argv(argv)
    if not tokens:
        return True
    for prefix in policy.command_blocklist:
        if len(prefix) > len(tokens):
            continue
        if all(tokens[i] == prefix[i] for i in range(len(prefix))):
            return True
    return False


def enforce_subprocess(
    policy: WatchdogPolicy,
    argv: str | Sequence[str],
    **kwargs: Any,
) -> subprocess.CompletedProcess:
    """Run *argv* under ``subprocess.run``, raising on policy violation.

    Pre-execution: ``is_command_blocked`` decides. Blocked commands
    raise ``SandboxPolicyViolation``; allowed commands flow through to
    ``subprocess.run(argv, **kwargs)``. The wrapper does not modify
    *kwargs* — caller controls timeouts, cwd, env, capture, etc.
    """
    if is_command_blocked(policy, argv):
        printable = " ".join(_split_argv(argv)) or "<empty>"
        raise SandboxPolicyViolation(
            f"command blocked by watchdog policy: {printable!r}"
        )
    return subprocess.run(argv, **kwargs)


__all__ = [
    "SandboxPolicyViolation",
    "VALID_NETWORK_POLICIES",
    "WatchdogPolicy",
    "enforce_subprocess",
    "is_command_blocked",
    "load_watchdog_policy",
]
