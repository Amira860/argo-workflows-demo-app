# Demo Repo Instructions

- Keep this repository lightweight and focused on validating Argo WorkflowTemplates from the separate library repository.
- Preserve the HTTP routes `/`, `/health`, `/api/catalog` and `/api/search` because multiple workflows and tests depend on them.
- Keep Kubernetes manifests under `k8s/base` and `k8s/overlays/*` consistent with the workflow library expectations.
- Prefer small, testable changes over framework-heavy additions.
- When changing deployment manifests, maintain compatibility with Kustomize overlays used by conditional, progressive, validated and rollback deployment workflows.
