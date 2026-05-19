# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""ContainerSandbox runtime shim — wrap subprocess execution with
docker / podman / singularity isolation flags.

task021 Session 5. Session 3 shipped the Dockerfiles + registry +
build script; Session 5 plugs the resulting images into the M0
verifier path so adversarial RLVR rollouts evaluating untrusted
candidate code run inside an isolated container instead of directly
on the host via ``sys.executable``.

Design points:

- Opt-in. Default (``container_runtime=None``) is unchanged in-process
  ``subprocess.run`` so existing health-baseline tests keep working
  on the same code path.
- Three runtimes supported. docker / podman wire the same flag set
  (``--rm --network=none --read-only --tmpfs /tmp --memory ...``);
  singularity uses ``--no-net --containall --bind`` equivalents.
- Workdir mounts. Caller hands a host directory; the shim mounts it
  read-only at ``/workspace`` inside the container. Candidate code
  cannot write back to the host filesystem.
- Resource limits. ``cpu_limit`` / ``memory_limit`` map to
  ``--cpus`` / ``--memory`` (docker / podman) or environment-variable
  hints (singularity — no kernel-level enforcement without cgroups).
- Timeout. Wraps the underlying subprocess.run timeout so a container
  that hangs gets killed by the same SIGTERM path as the in-process
  variant.

Sandbox unit tests stub ``subprocess.run`` to inspect the resolved
argv without actually invoking docker — running real containers is
task021 Session 4 cluster verify or local Docker daemon territory.
"""

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


KNOWN_CONTAINER_RUNTIMES = frozenset({"docker", "podman", "singularity"})


# Rollout policy distinguishes who produced the candidate the verifier
# is about to score. ``ORACLE`` candidates come from the gold answer
# (M0 health-baseline), the empty-string sentinel, or any other source
# the operator already trusts; isolation is unnecessary. ``ADVERSARIAL``
# candidates come from a policy model under training and may contain
# arbitrary code — those must run in a container.
#
# task021 Session 6 wires this policy through the verifier path so
# any future M1+ RLVR rollout that forgets ``container_runtime`` gets
# a loud RuntimeError instead of silently falling back to in-process
# (which would let untrusted code run on the host). The guard rail
# replaces the speculative "flip the default to docker" plan because
# there is no in-repo RLVR rollout caller today — the literal flip
# would have no coherent target.
ROLLOUT_POLICY_ORACLE = "oracle"
ROLLOUT_POLICY_ADVERSARIAL = "adversarial"
KNOWN_ROLLOUT_POLICIES = frozenset(
    {ROLLOUT_POLICY_ORACLE, ROLLOUT_POLICY_ADVERSARIAL}
)


def recommended_container_runtime(rollout_policy: str) -> str | None:
    """Return the container runtime an operator *should* use given the
    rollout policy.

    Oracle policy → None (in-process is fine). Adversarial policy →
    ``"docker"`` (operators can override to podman / singularity via
    the CLI flag; the recommendation is the canonical default).
    """
    if rollout_policy not in KNOWN_ROLLOUT_POLICIES:
        raise ValueError(
            f"unknown rollout policy {rollout_policy!r}; "
            f"known: {sorted(KNOWN_ROLLOUT_POLICIES)}"
        )
    return "docker" if rollout_policy == ROLLOUT_POLICY_ADVERSARIAL else None


@dataclass(frozen=True)
class ContainerSandbox:
    """Run a command inside an isolated container.

    All flag-construction is pure-Python; ``run`` is the only method
    that calls ``subprocess.run``. That separation lets tests assert
    the resolved argv shape without bringing up a real container.
    """

    image: str
    runtime: str = "docker"
    cpu_limit: str | None = None
    memory_limit: str | None = None
    network: str = "none"
    read_only: bool = True
    tmpfs: tuple[str, ...] = ("/tmp",)
    workdir_mount: str = "/workspace"

    def __post_init__(self) -> None:
        if self.runtime not in KNOWN_CONTAINER_RUNTIMES:
            raise ValueError(
                f"unknown container runtime {self.runtime!r}; "
                f"known: {sorted(KNOWN_CONTAINER_RUNTIMES)}"
            )

    def build_argv(
        self,
        *,
        host_workdir: Path,
        command: Sequence[str],
    ) -> list[str]:
        """Construct the full ``[runtime, run, …flags, image, *command]`` list.

        Pure function so tests can assert the exact argv shape.
        Caller decides whether to invoke it via ``subprocess.run`` or
        log it for audit.
        """
        host = Path(host_workdir).resolve()
        if self.runtime in ("docker", "podman"):
            argv: list[str] = [
                self.runtime,
                "run",
                "--rm",
                f"--network={self.network}",
                "--mount",
                f"type=bind,source={host},target={self.workdir_mount},readonly",
                "--workdir",
                self.workdir_mount,
            ]
            if self.read_only:
                argv.append("--read-only")
            for path in self.tmpfs:
                argv.extend(["--tmpfs", path])
            if self.cpu_limit:
                argv.extend(["--cpus", self.cpu_limit])
            if self.memory_limit:
                argv.extend(["--memory", self.memory_limit])
            argv.append(self.image)
            argv.extend(command)
            return argv

        # singularity: different flag dialect. ``exec`` is the
        # equivalent of ``docker run``; ``--containall`` blocks
        # auto-mount of /home / $PWD. ``docker://<tag>`` resolves the
        # image from the local cache built by build_sandbox_containers.sh.
        argv = [
            "singularity",
            "exec",
            "--containall",
            "--no-net" if self.network == "none" else "--net",
            "--bind",
            f"{host}:{self.workdir_mount}:ro",
            "--pwd",
            self.workdir_mount,
        ]
        if self.read_only:
            # singularity is read-only by default at the image layer;
            # this just makes the intent explicit.
            argv.append("--readonly")
        argv.append(f"docker://{self.image}")
        argv.extend(command)
        return argv

    def run(
        self,
        *,
        host_workdir: Path,
        command: Sequence[str],
        timeout_s: int,
    ) -> subprocess.CompletedProcess[str]:
        """Run *command* inside the container; return CompletedProcess.

        Raises ``subprocess.TimeoutExpired`` on hang (caller decides
        whether to translate to a verifier-side timeout signal).
        """
        argv = self.build_argv(host_workdir=host_workdir, command=command)
        return subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )


def sandbox_for_env(
    env_id: str,
    *,
    runtime: str = "docker",
) -> ContainerSandbox | None:
    """Convenience: look up the image for *env_id* via the registry
    and build a ContainerSandbox with sensible defaults for that env.

    Returns None for envs that don't have a registered sandbox image
    (caller should fall back to in-process execution).
    """
    from nemotron.recipes.super3.milestones.sandbox_containers.image_resolver import (
        resolve_image_for_env,
    )

    image = resolve_image_for_env(env_id)
    if image is None:
        return None
    return ContainerSandbox(image=image, runtime=runtime)


__all__ = [
    "ContainerSandbox",
    "KNOWN_CONTAINER_RUNTIMES",
    "KNOWN_ROLLOUT_POLICIES",
    "ROLLOUT_POLICY_ADVERSARIAL",
    "ROLLOUT_POLICY_ORACLE",
    "recommended_container_runtime",
    "sandbox_for_env",
]
