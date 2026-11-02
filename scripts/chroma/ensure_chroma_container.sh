#!/usr/bin/env bash
# Start (or create) the project ChromaDB Docker container.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/env.sh"

load_project_env "${ROOT_DIR}"
apply_chroma_defaults

# Python dependency chromadb 1.5.x requires server 1.5.x (0.6.x causes KeyError _type).
CHROMA_IMAGE="${EMPORIUM_CHROMA_IMAGE}"
if [[ "${CHROMA_IMAGE}" != chromadb/chroma:1.5.* ]]; then
  echo "[run] Using chromadb/chroma:1.5.9 (update EMPORIUM_CHROMA_IMAGE in .env; was ${CHROMA_IMAGE})."
  CHROMA_IMAGE="chromadb/chroma:1.5.9"
fi

DRY_RUN="${DRY_RUN:-0}"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required. Install Docker and run ./install.sh again." >&2
  exit 1
fi

if [[ "${DRY_RUN}" == "1" ]]; then
  echo "  -> ensure container ${EMPORIUM_CHROMA_CONTAINER} on port ${CHROMA_PORT} (${CHROMA_IMAGE})"
  exit 0
fi

_chroma_running_image() {
  docker inspect -f '{{.Config.Image}}' "${EMPORIUM_CHROMA_CONTAINER}" 2>/dev/null || true
}

_chroma_server_major() {
  local ver
  ver="$(curl -sf "http://127.0.0.1:${CHROMA_PORT}/api/v2/version" 2>/dev/null || true)"
  ver="${ver//\"/}"
  if [[ "${ver}" =~ ^([0-9]+)\. ]]; then
    echo "${BASH_REMATCH[1]}"
  fi
}

_needs_chroma_recreate() {
  local running_image="$1"
  if [[ "${running_image}" != "${CHROMA_IMAGE}" ]]; then
    return 0
  fi
  local major
  major="$(_chroma_server_major)"
  if [[ -n "${major}" && "${major}" -lt 1 ]]; then
    return 0
  fi
  return 1
}

if docker ps --format '{{.Names}}' | grep -qx "${EMPORIUM_CHROMA_CONTAINER}"; then
  running_image="$(_chroma_running_image)"
  if _needs_chroma_recreate "${running_image}"; then
    echo "[run] Chroma image mismatch (running ${running_image}, want ${CHROMA_IMAGE})."
    echo "      Recreating container (Python client chromadb 1.5.x requires server 1.5.x)..."
    docker stop "${EMPORIUM_CHROMA_CONTAINER}" >/dev/null
    docker rm "${EMPORIUM_CHROMA_CONTAINER}" >/dev/null
  else
    echo "[skip] Container '${EMPORIUM_CHROMA_CONTAINER}' already running."
    exit 0
  fi
elif docker ps -a --format '{{.Names}}' | grep -qx "${EMPORIUM_CHROMA_CONTAINER}"; then
  running_image="$(_chroma_running_image)"
  if _needs_chroma_recreate "${running_image}"; then
    echo "[run] Removing stale Chroma container (image ${running_image} != ${CHROMA_IMAGE})..."
    docker rm "${EMPORIUM_CHROMA_CONTAINER}" >/dev/null
  else
    echo "[run] Starting container '${EMPORIUM_CHROMA_CONTAINER}'..."
    docker start "${EMPORIUM_CHROMA_CONTAINER}"
    echo "[run] Waiting for ChromaDB..."
    health_url="http://127.0.0.1:${CHROMA_PORT}/api/v2/heartbeat"
    for _ in $(seq 1 60); do
      if command -v curl >/dev/null 2>&1 && curl -sf "${health_url}" >/dev/null 2>&1; then
        echo "[run] ChromaDB is ready."
        exit 0
      fi
      sleep 1
    done
    echo "Timed out waiting for ChromaDB." >&2
    exit 1
  fi
fi

if ! docker ps -a --format '{{.Names}}' | grep -qx "${EMPORIUM_CHROMA_CONTAINER}"; then
  echo "[run] Creating container '${EMPORIUM_CHROMA_CONTAINER}' (image ${CHROMA_IMAGE})..."
  docker run -d \
    --name "${EMPORIUM_CHROMA_CONTAINER}" \
    -p "${CHROMA_PORT}:8000" \
    -v "${EMPORIUM_CHROMA_VOLUME}:/data" \
    "${CHROMA_IMAGE}"
fi

echo "[run] Waiting for ChromaDB to accept connections..."
health_url="http://127.0.0.1:${CHROMA_PORT}/api/v2/heartbeat"
for _ in $(seq 1 60); do
  if command -v curl >/dev/null 2>&1 && curl -sf "${health_url}" >/dev/null 2>&1; then
    echo "[run] ChromaDB is ready."
    exit 0
  fi
  sleep 1
done

echo "Timed out waiting for ChromaDB in container '${EMPORIUM_CHROMA_CONTAINER}'." >&2
exit 1
