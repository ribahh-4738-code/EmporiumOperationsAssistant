#!/usr/bin/env bash
# Stop Emporium Postgres + Chroma + Admin containers (see .env for names/ports).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${ROOT_DIR}/scripts/docker/stop_project_containers.sh" "$@"
