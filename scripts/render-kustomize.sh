#!/usr/bin/env bash
set -euo pipefail

overlay="${1:-dev}"

case "$overlay" in
  dev|test|staging|prod|canary|green)
    ;;
  *)
    echo "Usage: bash scripts/render-kustomize.sh {dev|test|staging|prod|canary|green}" >&2
    exit 1
    ;;
esac

kubectl kustomize "k8s/overlays/$overlay"