#!/usr/bin/env bash
# Start (or create) ChromaDB Admin UI (unofficial Next.js UI for Chroma).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/env.sh"

load_project_env "${ROOT_DIR}"
apply_chroma_defaults

DRY_RUN="${DRY_RUN:-0}"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required. Install Docker and run ./install.sh again." >&2
  exit 1
fi

if [[ "${DRY_RUN}" == "1" ]]; then
  echo "  -> ensure container ${EMPORIUM_CHROMA_ADMIN_CONTAINER} on port ${CHROMA_ADMIN_PORT}"
  exit 0
fi

if docker ps --format '{{.Names}}' | grep -qx "${EMPORIUM_CHROMA_ADMIN_CONTAINER}"; then
  echo "[skip] Container '${EMPORIUM_CHROMA_ADMIN_CONTAINER}' already running."
  exit 0
fi

if docker ps -a --format '{{.Names}}' | grep -qx "${EMPORIUM_CHROMA_ADMIN_CONTAINER}"; then
  echo "[run] Starting container '${EMPORIUM_CHROMA_ADMIN_CONTAINER}'..."
  docker start "${EMPORIUM_CHROMA_ADMIN_CONTAINER}"
else
  echo "[run] Creating container '${EMPORIUM_CHROMA_ADMIN_CONTAINER}' (image ${EMPORIUM_CHROMA_ADMIN_IMAGE})..."
  docker run -d \
    --name "${EMPORIUM_CHROMA_ADMIN_CONTAINER}" \
    -p "${CHROMA_ADMIN_PORT}:3001" \
    --add-host=host.docker.internal:host-gateway \
    "${EMPORIUM_CHROMA_ADMIN_IMAGE}"
fi

echo "[run] ChromaDB Admin UI: http://127.0.0.1:${CHROMA_ADMIN_PORT}"
echo "      On first connect, use Chroma URL: http://host.docker.internal:${CHROMA_PORT}"
