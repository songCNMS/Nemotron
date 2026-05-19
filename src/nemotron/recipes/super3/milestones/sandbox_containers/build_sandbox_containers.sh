#!/usr/bin/env bash
# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Build the M1 sandbox container images declared in
# ``sandbox_image_registry.yaml``.
#
# Reads the registry, builds one image per row via the requested
# runtime (docker / podman / singularity). Runs locally on a dev
# workstation; ops integrate into CI / push to a registry on top.
#
# Usage:
#   ./build_sandbox_containers.sh                # docker, all images
#   ./build_sandbox_containers.sh --runtime podman
#   ./build_sandbox_containers.sh --only code_exec --runtime docker
#   ./build_sandbox_containers.sh --dry-run      # print the build commands
#
# Exit non-zero on first failure (no retries — operator handles).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY_PATH="${SCRIPT_DIR}/sandbox_image_registry.yaml"

RUNTIME="docker"
ONLY=""
DRY_RUN=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --runtime)
            RUNTIME="$2"
            shift 2
            ;;
        --only)
            ONLY="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        -h|--help)
            sed -n '4,18p' "${BASH_SOURCE[0]}"
            exit 0
            ;;
        *)
            echo "unknown flag: $1" >&2
            exit 2
            ;;
    esac
done

if [[ ! -f "${REGISTRY_PATH}" ]]; then
    echo "missing registry: ${REGISTRY_PATH}" >&2
    exit 2
fi

# Parse the registry via a tiny inline Python (yaml dependency only;
# avoids bash yaml parsing). Outputs one TSV line per image:
#   <image_id>\t<version_tag>\t<dockerfile_path>
parse_registry() {
    python3 - "${REGISTRY_PATH}" <<'PY'
import sys
import yaml

with open(sys.argv[1], encoding="utf-8") as f:
    data = yaml.safe_load(f)

for row in data.get("images", []):
    print(
        f"{row['image_id']}\t{row['version_tag']}\t{row['dockerfile_path']}"
    )
PY
}

build_one() {
    local image_id="$1"
    local version_tag="$2"
    local dockerfile_rel="$3"
    local dockerfile_abs="${SCRIPT_DIR}/${dockerfile_rel}"
    local tag="${image_id}:${version_tag}"

    if [[ ! -f "${dockerfile_abs}" ]]; then
        echo "missing Dockerfile: ${dockerfile_abs}" >&2
        return 1
    fi

    local -a cmd
    case "${RUNTIME}" in
        docker)
            cmd=(docker build -t "${tag}" -f "${dockerfile_abs}" "${SCRIPT_DIR}")
            ;;
        podman)
            cmd=(podman build -t "${tag}" -f "${dockerfile_abs}" "${SCRIPT_DIR}")
            ;;
        singularity)
            # Singularity needs a tagless name; emit a .sif next to the
            # Dockerfile. Ops can mv this into the cluster's sif_dir.
            local sif_path="${SCRIPT_DIR}/${image_id}_${version_tag}.sif"
            cmd=(singularity build "${sif_path}" "docker://${tag}")
            ;;
        *)
            echo "unknown runtime: ${RUNTIME}" >&2
            return 2
            ;;
    esac

    echo ">>> ${cmd[*]}"
    if [[ "${DRY_RUN}" -eq 0 ]]; then
        "${cmd[@]}"
    fi
}

parse_registry | while IFS=$'\t' read -r image_id version_tag dockerfile_rel; do
    if [[ -n "${ONLY}" && "${ONLY}" != "${image_id}" ]]; then
        continue
    fi
    build_one "${image_id}" "${version_tag}" "${dockerfile_rel}"
done

echo "build_sandbox_containers.sh: done"
