#!/usr/bin/env bash
# Append missing keys from .env.example to .env (does not overwrite existing keys).
set -euo pipefail

ensure_env_keys() {
  local root_dir="$1"
  local env_file="${root_dir}/.env"
  local example_file="${root_dir}/.env.example"

  if [[ ! -f "${example_file}" ]]; then
    return 0
  fi
  if [[ ! -f "${env_file}" ]]; then
    sed 's/\r$//' "${example_file}" > "${env_file}"
    echo "[run] Created ${env_file} from .env.example."
    return 0
  fi

  local added=0
  while IFS= read -r line || [[ -n "${line}" ]]; do
    line="${line//$'\r'/}"
    [[ -z "${line}" || "${line}" =~ ^[[:space:]]*# ]] && continue
    [[ "${line}" != *"="* ]] && continue
    local key="${line%%=*}"
    key="$(echo "${key}" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    if ! grep -q "^${key}=" "${env_file}" 2>/dev/null; then
      echo "${line}" >> "${env_file}"
      added=1
    fi
  done < "${example_file}"

  if [[ "${added}" == "1" ]]; then
    echo "[run] Appended missing keys from .env.example to .env (edit GEMINI_API_KEY)."
  fi
}
