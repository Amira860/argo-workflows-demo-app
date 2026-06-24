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
- `scripts/`: helper Bash and PowerShell scripts for local run and manifest rendering
- `k8s/bootstrap/`: lightweight bootstrap manifests for test namespaces

## Ubuntu test environment

Use [docs/ubuntu-argo-test-environment.md](docs/ubuntu-argo-test-environment.md) as the reference playbook for a single Ubuntu VM running Kubernetes and Argo Workflows.

## Local usage on Ubuntu

Install Python dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
npm ci
```

Run the app locally:

```bash
bash scripts/run-local.sh
```

Run Python tests:

```bash
pytest
```

Run Node tests:

```bash
npm run test:ci
```

## Local usage on Windows

Install Python dependencies:

```powershell
pip install -r requirements-dev.txt
npm ci
```

Run the app locally:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-local.ps1
```

Run tests:

```powershell
pytest
npm.cmd run test:ci
```

## Kubernetes usage

Create the namespaces used by the overlays and Argo:

```bash
kubectl apply -f k8s/bootstrap/namespaces.yaml
```

Render an overlay for inspection:

```bash
bash scripts/render-kustomize.sh prod
```

Apply an overlay manually with kubectl when testing on a cluster:

```bash
kubectl apply -n production -k k8s/overlays/prod
```

Run a simple compliance check before deployment:

```bash
kubectl kustomize k8s/overlays/prod | conftest test -p policies/compliance -
```

Smoke test a deployed environment:

```bash
kubectl port-forward svc/myapp 8080:80 -n test
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/api/catalog
curl 'http://127.0.0.1:8080/api/search?q=backend'
```

## Notes

- The default image repository is `docker.io/argoprojregistry/argo-workflows-demo-app`; build and push that image before testing deployments.
- The Ubuntu guide documents the recommended single-node `k3s` test environment for Argo Workflows.
- The `green` overlay is included to support blue/green switching tests from the workflow library.
- The database-related templates in the library still need a real PostgreSQL target and backup PVC to be exercised end-to-end.
