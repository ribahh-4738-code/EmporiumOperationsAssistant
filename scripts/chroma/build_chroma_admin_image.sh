#!/usr/bin/env bash
# Build local Chroma Admin UI image (API v2 compatible with chromadb/chroma:1.5.x).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/env.sh"

load_project_env "${ROOT_DIR}"
apply_chroma_defaults

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required." >&2
  exit 1
fi

TAG="${EMPORIUM_CHROMA_ADMIN_IMAGE:-emporium-chromadb-admin:1.5}"
echo "[run] Building ${TAG} (see docker/chromadb-admin/Dockerfile)..."
docker build -t "${TAG}" "${ROOT_DIR}/docker/chromadb-admin"
echo "[run] Done. Recreate Admin container if needed:"
echo "      docker rm -f ${EMPORIUM_CHROMA_ADMIN_CONTAINER} 2>/dev/null; ${ROOT_DIR}/scripts/chroma/ensure_chroma_admin_container.sh"
