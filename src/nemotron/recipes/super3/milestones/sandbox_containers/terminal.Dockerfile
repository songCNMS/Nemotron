# syntax=docker/dockerfile:1.7
#
# Terminal sandbox image for `terminal_basic_shell` and future
# `terminal_pivot` envs.
#
# Today M0 `terminal_basic_shell` verifier (`command_substring_match`)
# does not actually execute the candidate command — it just normalises
# the emitted string and substring-matches against the gold command.
# For M1+ `terminal_pivot` (NeMo-Gym tool-use loop running real bash
# commands against a sandbox) we need an isolated shell environment.
# This image is that environment.
#
# Caller must pass `--network=none --read-only --tmpfs /tmp` (or the
# Singularity equivalents) and SHOULD pass a bounded `--cpus` and
# `--memory` budget. The image alone does not enforce resource caps;
# that's the runtime's job (task021 Session 4 ContainerSandbox shim).
FROM alpine:3.20

# Install the shells + core utilities the candidate commands need.
# bash + coreutils for GNU semantics (mbpp / SWE-Bench style); busybox
# is on the base image already for the small commands.
RUN apk add --no-cache \
        bash \
        coreutils \
        findutils \
        grep \
        sed \
        gawk \
    && rm -rf /var/cache/apk/*

RUN adduser -D -u 1000 sandboxer
USER sandboxer
WORKDIR /home/sandboxer

# Smoke check baked in: print a known-good command output. Operators
# can run the bare image to confirm the shell + utilities landed
# before wiring it into the M1 terminal_pivot env.
CMD ["bash", "-c", "echo 'terminal sandbox ok'"]
