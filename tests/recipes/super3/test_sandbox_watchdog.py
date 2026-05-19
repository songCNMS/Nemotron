"""Tests for the SWE2 sandbox watchdog policy (task017 Session 2).

Covers:

- ``WatchdogPolicy`` dataclass surface
- ``load_watchdog_policy`` happy path + invalid network_policy +
  invalid blocklist shape + invalid resource limits
- ``is_command_blocked`` token-prefix matching: exact match / prefix
  match / non-match / case sensitivity
- ``enforce_subprocess`` raises on blocked, runs on allowed
- ``sandbox_watchdog_default.yaml`` loads + has sensible defaults
"""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


from nemotron.recipes.super3.milestones.m1_swe2.sandbox_watchdog import (  # noqa: E402
    VALID_NETWORK_POLICIES,
    SandboxPolicyViolation,
    WatchdogPolicy,
    enforce_subprocess,
    is_command_blocked,
    load_watchdog_policy,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_POLICY_PATH = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/milestones/m1_swe2/sandbox_watchdog_default.yaml"
)


def _write_policy(tmp_path: Path, text: str) -> Path:
    target = tmp_path / "policy.yaml"
    target.write_text(text, encoding="utf-8")
    return target


# ---------- Dataclass surface ----------


def test_valid_network_policies_lock_the_three_values() -> None:
    """The launcher cross-references this set when configuring egress;
    lock the values so a typo in a policy YAML doesn't silently get
    treated as a new mode."""
    assert VALID_NETWORK_POLICIES == frozenset({"deny", "allow_internal", "allow"})


def test_watchdog_policy_dataclass_defaults_to_deny_no_blocklist() -> None:
    policy = WatchdogPolicy()
    assert policy.command_blocklist == ()
    assert policy.network_policy == "deny"
    assert policy.cpu_limit is None
    assert policy.memory_limit_mb is None


# ---------- load_watchdog_policy ----------


def test_load_policy_happy_path_normalises_blocklist_entries(tmp_path: Path) -> None:
    policy_path = _write_policy(
        tmp_path,
        """
network_policy: deny
cpu_limit: 2
memory_limit_mb: 4096
command_blocklist:
  - "rm -rf /"
  - ["sudo", "-i"]
notes:
  - test policy
""",
    )
    policy = load_watchdog_policy(policy_path)
    assert policy.network_policy == "deny"
    assert policy.cpu_limit == pytest.approx(2.0)
    assert policy.memory_limit_mb == 4096
    assert ("rm", "-rf", "/") in policy.command_blocklist
    assert ("sudo", "-i") in policy.command_blocklist
    assert policy.notes == ("test policy",)


def test_load_policy_rejects_unknown_network_policy(tmp_path: Path) -> None:
    policy_path = _write_policy(tmp_path, "network_policy: yolo\n")
    with pytest.raises(ValueError, match="network_policy"):
        load_watchdog_policy(policy_path)


def test_load_policy_rejects_non_list_blocklist(tmp_path: Path) -> None:
    policy_path = _write_policy(
        tmp_path,
        "network_policy: deny\ncommand_blocklist: 'rm -rf /'\n",
    )
    with pytest.raises(ValueError, match="command_blocklist"):
        load_watchdog_policy(policy_path)


def test_load_policy_rejects_zero_or_negative_cpu_limit(tmp_path: Path) -> None:
    policy_path = _write_policy(tmp_path, "network_policy: deny\ncpu_limit: 0\n")
    with pytest.raises(ValueError, match="cpu_limit"):
        load_watchdog_policy(policy_path)


def test_load_policy_rejects_zero_memory_limit(tmp_path: Path) -> None:
    policy_path = _write_policy(
        tmp_path, "network_policy: deny\nmemory_limit_mb: 0\n"
    )
    with pytest.raises(ValueError, match="memory_limit_mb"):
        load_watchdog_policy(policy_path)


def test_load_policy_drops_malformed_blocklist_entries(tmp_path: Path) -> None:
    """A typo (None / empty string) in one entry shouldn't crash the
    whole policy load — drop the bad entry, keep the rest."""
    policy_path = _write_policy(
        tmp_path,
        """
network_policy: deny
command_blocklist:
  - "rm -rf /"
  - null
  - ""
  - ["sudo"]
""",
    )
    policy = load_watchdog_policy(policy_path)
    flat = {tuple(t) for t in policy.command_blocklist}
    assert ("rm", "-rf", "/") in flat
    assert ("sudo",) in flat
    # Null / empty entries dropped
    assert () not in flat


# ---------- is_command_blocked ----------


def _policy(*blocklist_tokens: tuple[str, ...]) -> WatchdogPolicy:
    return WatchdogPolicy(command_blocklist=tuple(blocklist_tokens))


def test_blocked_when_argv_starts_with_blocklist_prefix() -> None:
    policy = _policy(("rm", "-rf", "/"))
    assert is_command_blocked(policy, "rm -rf /") is True
    assert is_command_blocked(policy, ["rm", "-rf", "/"]) is True
    assert is_command_blocked(policy, "rm -rf / --extra-flag") is True


def test_not_blocked_when_argv_diverges_at_any_token() -> None:
    """Token-level prefix: `rm -rf /workspace` shares first two tokens
    with `rm -rf /` but the third token differs → not blocked."""
    policy = _policy(("rm", "-rf", "/"))
    assert is_command_blocked(policy, "rm -rf /workspace/build") is False


def test_not_blocked_when_argv_does_not_start_with_blocklist() -> None:
    policy = _policy(("sudo",))
    assert is_command_blocked(policy, "echo hello") is False
    assert is_command_blocked(policy, "/path/with/sudo/inside") is False


def test_blocked_for_empty_argv() -> None:
    """Empty argv is meaningless — block to surface the bug."""
    policy = _policy(("rm", "-rf"))
    assert is_command_blocked(policy, "") is True
    assert is_command_blocked(policy, []) is True


def test_blocked_is_case_sensitive_by_default() -> None:
    """Shells are case-sensitive; matching `RM` against `rm` would
    over-block. If a policy needs case-insensitive matching it's a
    separate feature."""
    policy = _policy(("rm",))
    assert is_command_blocked(policy, "rm foo") is True
    assert is_command_blocked(policy, "RM foo") is False


# ---------- enforce_subprocess ----------


def test_enforce_subprocess_raises_on_blocked_command(tmp_path: Path) -> None:
    policy = _policy(("rm", "-rf", "/"))
    with pytest.raises(SandboxPolicyViolation, match="blocked"):
        enforce_subprocess(policy, "rm -rf /")


def test_enforce_subprocess_runs_allowed_command(tmp_path: Path) -> None:
    """Allowed command flows through to subprocess.run; capture output
    via the standard subprocess kwargs."""
    policy = _policy(("sudo",))
    result = enforce_subprocess(
        policy, ["echo", "ok"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "ok"


# ---------- Default policy file ----------


def test_default_policy_yaml_loads_with_deny_network_and_blocks_rm_rf_root() -> None:
    """The shipped default must denylist the obvious-destructive
    commands; lock those so a future PR doesn't quietly relax them."""
    assert DEFAULT_POLICY_PATH.is_file()
    policy = load_watchdog_policy(DEFAULT_POLICY_PATH)
    assert policy.network_policy == "deny"
    # The exact destructive command must be blocked
    assert is_command_blocked(policy, "rm -rf /")
    # Privilege escalation must be blocked
    assert is_command_blocked(policy, "sudo whoami")
    # Network egress under deny policy
    assert is_command_blocked(policy, "curl https://example.com")
    # But scoped rm inside a workdir is NOT blocked (token-prefix rule)
    assert not is_command_blocked(policy, "rm -rf /workspace/.cache")
