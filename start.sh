#!/usr/bin/env bash
set -e

if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python 3.10+ is required but python3/python was not found in PATH."
    echo "Please install Python 3.10 or higher."
    exit 1
fi

exec "$PYTHON_CMD" start.py "$@"
