#!/usr/bin/env bash
# Thin wrapper around `docker buildx bake` (see docker-bake.hcl).
# Prefer calling bake directly:  docker buildx bake <target>
#
# Usage:
#   bash build.sh                 # build every image
#   bash build.sh airflow         # build one target (+ its deps)
#   bash build.sh spark           # build the "spark" group
set -euo pipefail

cd "$(dirname "$0")"

exec docker buildx bake -f docker-bake.hcl "$@"
