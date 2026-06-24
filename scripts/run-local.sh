#!/usr/bin/env bash
set -euo pipefail

export APP_ENV="${APP_ENV:-dev}"
export APP_VERSION="${APP_VERSION:-0.1.0}"

exec "${PYTHON_BIN:-python3}" wsgi.py