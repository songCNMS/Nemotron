# syntax=docker/dockerfile:1.7
#
# Lean sandbox image for `math_formal_lean` env's real Lean compiler
# verification.
#
# task056 Session 2 shipped the M0 `lean_proof_stub` verifier which
# only checks the candidate proof is non-empty. The real verifier
# wants to compile the candidate proof against mathlib4 and confirm
# `#print axioms <theorem>` is clean (no `sorry`, no new axioms). That
# requires the Lean toolchain inside an isolated container — this
# image.
#
# Wiring is task017 / task049 territory; this image is the first
# missing piece for that work to be sandbox-runnable on a developer
# workstation (`docker run --rm lean:v0.1 lean --version`).
#
# Build size warning: a full mathlib4 cache is ~7 GB at HEAD. We do
# *not* pre-build it here; ops layer that on top via a derived image
# or volume mount. This image just gives you working `lean` + `lake`.
FROM debian:bookworm-slim

# elan is the official Lean toolchain manager. We install it as root
# then drop to UID 1000 so the running candidate code can't tamper
# with /usr/local.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install elan + Lean 4 stable. Pinning to a specific elan release
# tag rather than `master` so the build is reproducible.
ENV ELAN_HOME=/opt/elan \
    PATH="/opt/elan/bin:${PATH}"
RUN curl --proto '=https' --tlsv1.2 -sSf \
        -L https://raw.githubusercontent.com/leanprover/elan/v3.1.1/elan-init.sh \
      | sh -s -- --default-toolchain leanprover/lean4:stable -y --no-modify-path \
    && lean --version

# Strip out curl + apt cache *after* elan is installed so the candidate
# code can't fetch arbitrary URLs at run time.
RUN apt-get purge -y curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

RUN useradd --create-home --uid 1000 sandboxer
USER sandboxer
WORKDIR /home/sandboxer

# Smoke check baked in: print Lean version. Operators can run the
# bare image to confirm the toolchain landed before wiring it into
# the M0 / M1 verifier path.
CMD ["lean", "--version"]
