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

_chroma_admin_image_present() {
  docker image inspect "${EMPORIUM_CHROMA_ADMIN_IMAGE}" >/dev/null 2>&1
}

if ! _chroma_admin_image_present; then
  echo "[run] Admin image '${EMPORIUM_CHROMA_ADMIN_IMAGE}' not found; building (Chroma 1.5 needs API v2 UI)..."
  "${ROOT_DIR}/scripts/chroma/build_chroma_admin_image.sh"
fi

_admin_port_holder() {
  docker ps --format '{{.Names}}' --filter "publish=${CHROMA_ADMIN_PORT}" 2>/dev/null | head -1
}

_port_blocked_by_other() {
  local holder
  holder="$(_admin_port_holder)"
  if [[ -z "${holder}" ]]; then
    return 1
  fi
  if [[ "${holder}" == "${EMPORIUM_CHROMA_ADMIN_CONTAINER}" ]]; then
    return 1
  fi
  echo "${holder}"
  return 0
}

if docker ps --format '{{.Names}}' | grep -qx "${EMPORIUM_CHROMA_ADMIN_CONTAINER}"; then
  running_image="$(docker inspect -f '{{.Config.Image}}' "${EMPORIUM_CHROMA_ADMIN_CONTAINER}" 2>/dev/null || true)"
  if [[ "${running_image}" != "${EMPORIUM_CHROMA_ADMIN_IMAGE}" ]]; then
    echo "[run] Admin container uses image '${running_image}'; want '${EMPORIUM_CHROMA_ADMIN_IMAGE}'. Recreating..."
    docker rm -f "${EMPORIUM_CHROMA_ADMIN_CONTAINER}" >/dev/null
  else
    echo "[skip] Container '${EMPORIUM_CHROMA_ADMIN_CONTAINER}' already running."
    exit 0
  fi
fi

if other="$(_port_blocked_by_other)"; then
  echo "[warn] Port ${CHROMA_ADMIN_PORT} is already in use by Docker container '${other}'." >&2
  echo "[warn] Chroma API (port ${CHROMA_PORT}) and RAG are unaffected; Admin UI is optional." >&2
  echo "[warn] Use another host port (recommended — no need to stop ${other}):" >&2
  echo "       Set CHROMA_ADMIN_PORT=3002 in .env, then:" >&2
  echo "       docker rm -f ${EMPORIUM_CHROMA_ADMIN_CONTAINER} 2>/dev/null; $0" >&2
  exit 0
fi

if docker ps -a --format '{{.Names}}' | grep -qx "${EMPORIUM_CHROMA_ADMIN_CONTAINER}"; then
  running_image="$(docker inspect -f '{{.Config.Image}}' "${EMPORIUM_CHROMA_ADMIN_CONTAINER}" 2>/dev/null || true)"
  if [[ "${running_image}" != "${EMPORIUM_CHROMA_ADMIN_IMAGE}" ]]; then
    echo "[run] Removing Admin container (image '${running_image}' != '${EMPORIUM_CHROMA_ADMIN_IMAGE}')..."
    docker rm -f "${EMPORIUM_CHROMA_ADMIN_CONTAINER}" >/dev/null
  else
  echo "[run] Starting container '${EMPORIUM_CHROMA_ADMIN_CONTAINER}'..."
  if ! docker start "${EMPORIUM_CHROMA_ADMIN_CONTAINER}" 2>/dev/null; then
    if other="$(_port_blocked_by_other)"; then
      echo "[warn] Could not start Admin UI: port ${CHROMA_ADMIN_PORT} held by '${other}'." >&2
      echo "[warn] See options above (CHROMA_ADMIN_PORT or docker stop)." >&2
      exit 0
    fi
    echo "Failed to start '${EMPORIUM_CHROMA_ADMIN_CONTAINER}'." >&2
    exit 1
  fi
  fi
else
  echo "[run] Creating container '${EMPORIUM_CHROMA_ADMIN_CONTAINER}' (image ${EMPORIUM_CHROMA_ADMIN_IMAGE})..."
  platform_args=()
  if [[ "$(uname -m)" == "x86_64" || "$(uname -m)" == "amd64" ]]; then
    platform_args=(--platform linux/amd64)
  fi
  if ! docker run -d \
    "${platform_args[@]}" \
    --name "${EMPORIUM_CHROMA_ADMIN_CONTAINER}" \
    -p "${CHROMA_ADMIN_PORT}:${CHROMA_ADMIN_CONTAINER_PORT}" \
    --add-host=host.docker.internal:host-gateway \
    "${EMPORIUM_CHROMA_ADMIN_IMAGE}"; then
    if other="$(_port_blocked_by_other)"; then
      echo "[warn] Could not create Admin UI: port ${CHROMA_ADMIN_PORT} held by '${other}'." >&2
      docker rm -f "${EMPORIUM_CHROMA_ADMIN_CONTAINER}" 2>/dev/null || true
      exit 0
    fi
    exit 1
  fi
fi

if ! docker ps --format '{{.Names}}' | grep -qx "${EMPORIUM_CHROMA_ADMIN_CONTAINER}"; then
  echo "[warn] Admin container exited immediately (common cause: ARM-only image on amd64)." >&2
  docker logs "${EMPORIUM_CHROMA_ADMIN_CONTAINER}" 2>&1 | tail -5 >&2 || true
  echo "[warn] Build the v2-compatible UI: ${ROOT_DIR}/scripts/chroma/build_chroma_admin_image.sh" >&2
  exit 0
fi

echo "[run] ChromaDB Admin UI: http://127.0.0.1:${CHROMA_ADMIN_PORT}"
echo "      Setup → Chroma URL: http://host.docker.internal:${CHROMA_PORT}"
echo "      Tenant: default_tenant   Database: default_database"
echo "      (Not 'default' — Chroma 1.5 returns 500 in the UI if tenant/database are wrong.)"
