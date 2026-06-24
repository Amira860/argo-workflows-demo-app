# Workflow Library Test Plan

This document defines the recommended step-by-step test campaign for the Argo workflow library against this demo application.

## Preconditions

- Argo Workflows is installed and the library templates are loaded in namespace `argo-lab`.
- The demo application repository is reachable at `https://github.com/Amira860/argo-workflows-demo-app.git`.
- The demo app image exists in Docker Hub as `docker.io/argoprojregistry/argo-workflows-demo-app`.
- The demo app has already been validated manually in namespaces `test`, `staging`, `production`, `canary`, and `green`.
- The Kubernetes service DNS names below are reachable from workflow pods:
  - `http://myapp.test.svc.cluster.local/health`
  - `http://myapp.staging.svc.cluster.local/health`
  - `http://myapp.production.svc.cluster.local/health`

## Library Fixes To Publish First

Before running the campaign on the VM, publish the local fixes made in the workflow library repository for these files:

- `templates/infra/wt-namespace-bootstrap.yaml`
- `templates/monitoring/wt-notification.yaml`
- `templates/data/wt-data-pipeline.yaml`
- `templates/deployments/wt-api-protection.yaml`
- `templates/deployments/wt-rollback-on-failure.yaml`

## Phase 1: Immediate Template Tests

### 1. Access validation via kubectl

```bash
argo submit -n argo-lab --from workflowtemplate/wt-access-validation-simple \
  -p target-namespace=test \
  -p verb=get \
  -p resource=pods \
  --watch
```

### 2. Access validation via SelfSubjectAccessReview

```bash
argo submit -n argo-lab --from workflowtemplate/wt-access-validation \
  -p target-namespace=test \
  -p verb=get \
  -p resource=pods \
  --watch
```

### 3. Human validation flow

```bash
argo submit -n argo-lab --from workflowtemplate/wt-human-validation \
  -p change-id=CHG-DEMO-001 \
  -p target-environment=production

argo list -n argo-lab
argo resume -n argo-lab @latest
```

### 4. Error classification in simulated mode

```bash
argo submit -n argo-lab --from workflowtemplate/wt-error-classification \
  -p simulated-mode=timeout \
  --watch

argo submit -n argo-lab --from workflowtemplate/wt-error-classification \
  -p simulated-mode=http500 \
  --watch

argo submit -n argo-lab --from workflowtemplate/wt-error-classification \
  -p simulated-mode=config \
  --watch
```

### 5. Error classification against the real app

```bash
argo submit -n argo-lab --from workflowtemplate/wt-error-classification \
  -p simulated-mode=none \
  -p target-url=http://myapp.staging.svc.cluster.local/health \
  --watch
```

### 6. Incident diagnostic on the test namespace

```bash
argo submit -n argo-lab --from workflowtemplate/wt-incident-diagnostic \
  -p namespace=test \
  -p app-label=myapp \
  -p incident-id=INC-DEMO-001 \
  --watch
```

### 7. Self-contained data pipeline

```bash
argo submit -n argo-lab --from workflowtemplate/wt-data-pipeline --watch
```

### 8. Kubernetes resource job

```bash
argo submit -n argo-lab --from workflowtemplate/wt-k8s-resource-job \
  -p namespace=test \
  -p job-name-prefix=argo-maint- \
  -p image=alpine:3.19 \
  -p job-script="echo start; sleep 5; echo done" \
  --watch
```

### 9. Namespace bootstrap in a sandbox namespace

```bash
argo submit -n argo-lab --from workflowtemplate/wt-namespace-bootstrap \
  -p namespace=team-sandbox \
  -p quota-pods=10 \
  --watch
```

## Phase 2: Demo App Operational Tests

### 10. Service health check on test

```bash
argo submit -n argo-lab --from workflowtemplate/wt-service-health-check \
  -p service-name=myapp \
  -p service-url=http://myapp.test.svc.cluster.local/health \
  -p expected-status-code=200 \
  --watch
```

### 11. Service health check on staging

```bash
argo submit -n argo-lab --from workflowtemplate/wt-service-health-check \
  -p service-name=myapp \
  -p service-url=http://myapp.staging.svc.cluster.local/health \
  -p expected-status-code=200 \
  --watch
```

### 12. Cache warmup on test

```bash
argo submit -n argo-lab --from workflowtemplate/wt-cache-warmup \
  -p base-url=http://myapp.test.svc.cluster.local \
  -p warmup-paths='["/","/health","/api/catalog","/api/search?q=backend"]' \
  --watch
```

### 13. Multi-service smoke tests across environments

```bash
argo submit -n argo-lab --from workflowtemplate/wt-multi-service-smoke-tests \
  -p target-matrix='[
    {"name":"test","url":"http://myapp.test.svc.cluster.local/health","expected_status":"200"},
    {"name":"staging","url":"http://myapp.staging.svc.cluster.local/health","expected_status":"200"},
    {"name":"prod","url":"http://myapp.production.svc.cluster.local/health","expected_status":"200"}
  ]' \
  --watch
```

### 14. Notification exit handler without webhook

```bash
argo submit -n argo-lab --from workflowtemplate/wt-notification-exit \
  -p operation-name=demo-health-check \
  -p target-environment=production \
  -p target-url=http://myapp.production.svc.cluster.local/health \
  -p attempts=1 \
  --watch
```

### 15. Optional TLS secret scan

```bash
argo submit -n argo-lab --from workflowtemplate/wt-secret-expiry-check \
  -p namespace=argo-lab \
  -p warning-days=30 \
  --watch
```

## Phase 3: Repo-Driven Deployment Tests

### 16. Server-side manifest validation

```bash
argo submit -n argo-lab --from workflowtemplate/wt-server-side-manifest-validation \
  -p repo-url=https://github.com/Amira860/argo-workflows-demo-app.git \
  -p branch=main \
  -p namespace=production \
  -p manifests-path=k8s/overlays/prod \
  --watch
```

### 17. Compliance check with deploy on success

```bash
argo submit -n argo-lab --from workflowtemplate/wt-compliance-check \
  -p repo-url=https://github.com/Amira860/argo-workflows-demo-app.git \
  -p branch=main \
  -p manifests-path=k8s/overlays/prod \
  -p policy-path=policies/compliance \
  -p namespace=production \
  -p app-name=myapp \
  --watch
```

### 18. Conditional deployment by environment

```bash
argo submit -n argo-lab --from workflowtemplate/wt-conditional-deployment \
  -p repo-url=https://github.com/Amira860/argo-workflows-demo-app.git \
  -p branch=main \
  -p env=test \
  -p app-name=myapp \
  -p namespace-dev=dev \
  -p namespace-test=test \
  -p namespace-prod=production \
  --watch
```

Repeat with `env=dev` and `env=prod`.

### 19. Validated deployment with approval gate

```bash
argo submit -n argo-lab --from workflowtemplate/wt-validated-deployment \
  -p repo-url=https://github.com/Amira860/argo-workflows-demo-app.git \
  -p branch=main \
  -p app-name=myapp \
  -p staging-namespace=staging \
  -p prod-namespace=production

argo list -n argo-lab
argo resume -n argo-lab @latest
```

### 20. API protection from staging to production

```bash
argo submit -n argo-lab --from workflowtemplate/wt-api-protection \
  -p repo-url=https://github.com/Amira860/argo-workflows-demo-app.git \
  -p branch=main \
  -p app-name=myapp \
  -p staging-namespace=staging \
  -p prod-namespace=production \
  -p staging-url=http://myapp.staging.svc.cluster.local/health \
  -p total-checks=5 \
  -p max-failures=0 \
  -p expected-status-code=200 \
  --watch
```

### 21. Blue/green switch

Deploy green first if needed:

```bash
kubectl apply -k k8s/overlays/green
kubectl rollout status deployment/myapp-green -n production
```

Then run the workflow:

```bash
argo submit -n argo-lab --from workflowtemplate/wt-blue-green-switch \
  -p namespace=production \
  -p app-name=myapp \
  -p green-deployment-name=myapp-green \
  -p service-name=myapp \
  -p smoke-test-url=http://myapp.production.svc.cluster.local/health

argo list -n argo-lab
argo resume -n argo-lab @latest
```

### 22. Rollback on failure

Success case:

```bash
argo submit -n argo-lab --from workflowtemplate/wt-rollback-on-failure \
  -p repo-url=https://github.com/Amira860/argo-workflows-demo-app.git \
  -p branch=main \
  -p app-name=myapp \
  -p container-name=myapp \
  -p namespace=production \
  -p deploy-overlay-path=k8s/overlays/prod \
  -p smoke-test-url=http://myapp.production.svc.cluster.local/health \
  --watch
```

Rollback case with a deliberately invalid tag:

```bash
argo submit -n argo-lab --from workflowtemplate/wt-rollback-on-failure \
  -p repo-url=https://github.com/Amira860/argo-workflows-demo-app.git \
  -p branch=main \
  -p app-name=myapp \
  -p container-name=myapp \
  -p namespace=production \
  -p deploy-overlay-path=k8s/overlays/prod \
  -p image=docker.io/argoprojregistry/argo-workflows-demo-app:does-not-exist \
  -p smoke-test-url=http://myapp.production.svc.cluster.local/health \
  -p rollback-enabled=true \
  --watch
```

## Phase 4: Deferred Tests

These templates still need additional setup before they are meaningful:

- `wt-ci-cd-pipeline`: needs registry credentials and a `ReadWriteMany` storage class.
- `wt-distributed-tests`: needs `ReadWriteMany` storage and a realistic perf target.
- `wt-progressive-deployment`: needs alignment between the workflow semantics and the demo app canary promotion model.
- `wt-postgres-backup`, `wt-postgres-restore`, `cw-postgres-backup`, `wt-db-migration-with-backup`: need PostgreSQL plus secrets and PVC.
- `wt-log-cleanup`, `cw-log-cleanup`: need a log PVC with files to clean.

## Suggested Execution Order

1. Run all of Phase 1.
2. Run all of Phase 2.
3. Run Phase 3 in numeric order.
4. Stop on the first real failure and inspect `argo logs`, `kubectl get pods`, `kubectl describe`, and the generated artifacts.