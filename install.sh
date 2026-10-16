#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${1:-$(pwd)}"
PROJECT="${2:-}"

echo "=========================================================="
echo "  HyperFrames Short Producer - Instalador de Entorno y Skills"
echo "=========================================================="

if [ -n "$PROJECT" ]; then
  python3 "$SCRIPT_DIR/scripts/setup_env.py" --workspace "$WORKSPACE" --project "$PROJECT"
else
  python3 "$SCRIPT_DIR/scripts/setup_env.py" --workspace "$WORKSPACE"
fi
