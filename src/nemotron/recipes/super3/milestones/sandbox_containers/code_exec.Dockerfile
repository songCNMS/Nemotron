# syntax=docker/dockerfile:1.7
#
# code_exec sandbox image for the M0 `code_execution_python` env's
# `python_unit_tests` verifier.
#
# Today the verifier (`run_m0_health_baseline.run_python_unit_tests`)
# runs `sys.executable -I` directly on the host. For oracle health
# baselines that's fine; for M1+ RLVR rollouts evaluating adversarial
# policy outputs that's not — the candidate code runs with the
# operator's full filesystem + network access.
#
# This image wraps Python 3.12-slim with:
#   - non-root user (UID 1000)
#   - no compilers, no curl, no pip wheels staged in (caller pre-mounts
#     a writable /workspace if it needs to)
#   - pytest preinstalled for `pytest -q` style runs (mbpp test_list
#     uses plain assert, so pytest is overkill but cheap to ship)
#
# Caller must pass `--network=none --read-only --tmpfs /tmp` (or the
# Singularity equivalents) to enforce isolation. The image alone does
# not prevent network egress; that's the runtime's job. See
# task021 Session 4 ContainerSandbox shim for the wiring.
FROM python:3.12-slim

# Install pytest at the system level (no venv); the running user has
# read-only access so they can't tamper with the install.
RUN pip install --no-cache-dir --disable-pip-version-check pytest==8.3.3 \
    && python -c "import pytest; print(pytest.__version__)"

# Drop privileges. UID 1000 mirrors the convention most CI runners use.
RUN useradd --create-home --uid 1000 sandboxer
USER sandboxer
WORKDIR /home/sandboxer

# A minimal smoke check baked into the image: when run with no command
# the entrypoint asserts pytest is importable. That gives operators a
# fast "is the image healthy?" probe before pushing it to a registry.
CMD ["python", "-c", "import pytest, sys; sys.stdout.write(f'pytest {pytest.__version__} ok\\n')"]
