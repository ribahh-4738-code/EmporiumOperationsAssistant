#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/env.sh"

load_project_env "${ROOT_DIR}"
apply_postgres_defaults
export POSTGRES_HOST POSTGRES_PORT POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB
export ASSISTANT_DISPLAY_NAME="${ASSISTANT_DISPLAY_NAME:-Maiara}"
export ASSISTANT_PROFILE_NAME="${ASSISTANT_PROFILE_NAME:-maiara}"

DRY_RUN="${DRY_RUN:-0}"
VENV_PYTHON="${ROOT_DIR}/.venv/bin/python"

if [[ "${DRY_RUN}" == "1" ]]; then
  echo "  -> seed assistant profile and module prompts (idempotent)"
  exit 0
fi

if [[ ! -x "${VENV_PYTHON}" ]]; then
  echo "Virtualenv not found. Run ./install.sh first." >&2
  exit 1
fi

if ( cd "${ROOT_DIR}" && "${VENV_PYTHON}" - <<'PY'
import json
from pathlib import Path
from emporium_operations_assistant.assistant.repository import AssistantRepository
from emporium_operations_assistant.config import load_settings

settings = load_settings()
data = json.loads(
    Path("db/seed/assistant/default.json").read_text(encoding="utf-8")
)
keys = [p["module_key"] for p in data.get("prompts", [])]
repo = AssistantRepository(settings)
complete = repo.profile_seed_complete(settings.assistant_profile_name, keys)
raise SystemExit(0 if complete else 1)
PY
); then
  echo "[skip] Assistant seed already complete."
  exit 0
fi

"${VENV_PYTHON}" -m emporium_operations_assistant.assistant.seed_defaults
