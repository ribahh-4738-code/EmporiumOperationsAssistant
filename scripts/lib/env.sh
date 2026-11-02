#!/usr/bin/env bash
# Shared environment loading for Emporium Operations Assistant scripts.
set -euo pipefail

env_root_dir() {
  local script_path="${BASH_SOURCE[1]:-${BASH_SOURCE[0]}}"
  cd "$(dirname "${script_path}")/../.." && pwd
}

load_project_env() {
  local root_dir="$1"
  local env_file="${root_dir}/.env"
  if [[ -f "${env_file}" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "${env_file}"
    set +a
  fi
}

apply_postgres_defaults() {
  POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
  POSTGRES_PORT="${POSTGRES_PORT:-5435}"
  POSTGRES_USER="${POSTGRES_USER:-postgres}"
  POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-emporium_dev}"
  POSTGRES_DB="${POSTGRES_DB:-emporium_operation}"
  EMPORIUM_DOCKER_CONTAINER="${EMPORIUM_DOCKER_CONTAINER:-emporium_ops_postgres}"
  EMPORIUM_DOCKER_IMAGE="${EMPORIUM_DOCKER_IMAGE:-postgres:16-alpine}"
  EMPORIUM_DOCKER_VOLUME="${EMPORIUM_DOCKER_VOLUME:-emporium_ops_pgdata}"
}

apply_chroma_defaults() {
  CHROMA_HOST="${CHROMA_HOST:-localhost}"
  CHROMA_PORT="${CHROMA_PORT:-8001}"
  CHROMA_COLLECTION="${CHROMA_COLLECTION:-store_policies}"
  RAG_TOP_K="${RAG_TOP_K:-5}"
  RAG_CHUNK_SIZE="${RAG_CHUNK_SIZE:-900}"
  RAG_CHUNK_OVERLAP="${RAG_CHUNK_OVERLAP:-120}"
  GEMINI_EMBEDDING_MODEL="${GEMINI_EMBEDDING_MODEL:-text-embedding-004}"
  EMPORIUM_CHROMA_CONTAINER="${EMPORIUM_CHROMA_CONTAINER:-emporium_ops_chroma}"
  EMPORIUM_CHROMA_IMAGE="${EMPORIUM_CHROMA_IMAGE:-chromadb/chroma:1.5.9}"
  EMPORIUM_CHROMA_VOLUME="${EMPORIUM_CHROMA_VOLUME:-emporium_ops_chromadata}"
  EMPORIUM_CHROMA_ADMIN_CONTAINER="${EMPORIUM_CHROMA_ADMIN_CONTAINER:-emporium_ops_chroma_admin}"
  EMPORIUM_CHROMA_ADMIN_IMAGE="${EMPORIUM_CHROMA_ADMIN_IMAGE:-fengzhichao/chromadb-admin:latest}"
  CHROMA_ADMIN_PORT="${CHROMA_ADMIN_PORT:-3001}"
}

export_pg_vars() {
  export PGHOST="${POSTGRES_HOST}"
  export PGPORT="${POSTGRES_PORT}"
  export PGUSER="${POSTGRES_USER}"
  export PGPASSWORD="${POSTGRES_PASSWORD}"
}
