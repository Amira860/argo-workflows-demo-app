# Argo Workflows Demo App

This repository is a separate local demo project used to test the WorkflowTemplates from the workflow library repository on another Kubernetes cluster.

## Purpose

This project is intentionally small but structured to exercise concrete workflow cases:

- CI/CD pipeline with Python unit and integration tests
- parallel testing with Python API tests and Node-based UI contract tests
- conditional, validated and progressive deployments using Kustomize overlays
- compliance checks using Conftest/OPA policies
- API protection, smoke tests and cache warmup workflows
- rollback and blue/green style deployment experiments
- database-related workflow scenarios with backup and restore placeholders

## Structure

- `app/`: minimal Flask application with `/`, `/health`, `/api/catalog` and `/api/search`
- `tests/unit/`: fast unit tests
- `tests/integration/`: integration tests against a live local server fixture
- `tests/api/`: API checks used by distributed test workflows
- `tests/ui/`: lightweight Node test suite used by `npm ci` and `npm run test:ci`
- `k8s/base/`: base Deployment and Service manifests
- `k8s/overlays/`: overlays for `dev`, `test`, `staging`, `prod`, `canary` and `green`
- `policies/compliance/`: sample Conftest policies
- `scripts/`: helper PowerShell scripts for local run and image build

## Local usage

Install Python dependencies:

```powershell
pip install -r requirements-dev.txt
```

Run the app locally:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-local.ps1
```

Run Python tests:

```powershell
pytest
```

Run Node tests:

```powershell
npm ci
npm run test:ci
```

## Kubernetes usage

Render an overlay for inspection:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/render-kustomize.ps1 -Overlay prod
```

Apply an overlay manually with kubectl when testing on a cluster:

```powershell
kubectl apply -n production -k k8s/overlays/prod
```

## Notes

- Image names and registries are placeholders and should be adapted before pushing to a real registry.
- The `green` overlay is included to support blue/green switching tests from the workflow library.
- The database-related templates in the library still need a real PostgreSQL target and backup PVC to be exercised end-to-end.
