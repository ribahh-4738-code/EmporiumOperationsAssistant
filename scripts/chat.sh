#!/usr/bin/env bash
# Deprecated path — use ./chat.sh at repository root.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "${ROOT_DIR}/chat.sh" "$@"
