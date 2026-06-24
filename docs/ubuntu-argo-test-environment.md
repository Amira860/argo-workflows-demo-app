# Ubuntu Argo Test Environment

This document defines the target environment for testing the WorkflowTemplates against this demo application.

## Target topology

- One Ubuntu VM dedicated to test execution.
- One single-node Kubernetes cluster on that VM, using `k3s` for a lightweight setup.
- One Argo Workflows installation in the `argo` namespace.
- Application deployments in `dev`, `test`, `staging` and `production`.
- A container registry reachable by the VM and the cluster.

## Recommended VM sizing

- Ubuntu 22.04 LTS or Ubuntu 24.04 LTS.
- 4 vCPU minimum.
- 8 GiB RAM minimum.
- 30 GiB disk minimum.

## Tools to install on Ubuntu

Update the OS first:

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

Install common packages:

```bash
sudo apt-get install -y ca-certificates curl git jq unzip python3 python3-pip python3-venv
```

Install Node.js 20:

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

Install Docker for local image builds:

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"
```

Open a new shell session after the Docker group change.

## Install Kubernetes with k3s

Install `k3s`:

```bash
curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
```

Point `kubectl` to the cluster:

```bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
kubectl get nodes
```

Persist that kubeconfig in your shell profile if this VM will be used interactively.

## Install Argo Workflows

Create the namespace first:

```bash
kubectl create namespace argo --dry-run=client -o yaml | kubectl apply -f -
```

Install Argo Workflows in `argo`:

```bash
kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/v3.5.11/quick-start-minimal.yaml
```

Wait for the controllers and the server:

```bash
kubectl get pods -n argo
```

Install the Argo CLI:

```bash
curl -sLO https://github.com/argoproj/argo-workflows/releases/download/v3.5.11/argo-linux-amd64.gz
gunzip argo-linux-amd64.gz
chmod +x argo-linux-amd64
sudo mv argo-linux-amd64 /usr/local/bin/argo
argo version
```

If your workflow library requires a different Argo version, pin that version here and keep the CLI and controller aligned.

## Install Conftest

```bash
curl -sL https://github.com/open-policy-agent/conftest/releases/download/v0.54.0/conftest_0.54.0_Linux_x86_64.tar.gz | tar -xz
sudo mv conftest /usr/local/bin/conftest
conftest --version
```

## Clone and bootstrap the demo repository

```bash
git clone <your-demo-repo-url>
cd argo-workflows-demo-app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
npm ci
chmod +x scripts/*.sh
```

Validate the repo locally before touching the cluster:

```bash
pytest
npm run test:ci
bash scripts/render-kustomize.sh test > /tmp/demo-test.yaml
conftest test -p policies/compliance /tmp/demo-test.yaml
```

## Prepare the cluster namespaces

Apply the bootstrap manifest once:

```bash
kubectl apply -f k8s/bootstrap/namespaces.yaml
kubectl get ns argo dev test staging production
```

## Prepare the application image

The Kubernetes overlays are configured to use `docker.io/argoprojregistry/argo-workflows-demo-app`. Push that image before running deployment workflows.

Recommended path:

1. Log in to Docker Hub with the `argoprojregistry` account.
2. Build and push the image.
3. Publish the environment tags used by the overlays.

Example:

```bash
docker login
docker build -t docker.io/argoprojregistry/argo-workflows-demo-app:0.1.0 .
docker push docker.io/argoprojregistry/argo-workflows-demo-app:0.1.0
```

If the Docker Hub repository does not exist yet, the first successful push creates it. You can also create it manually in the Docker Hub UI.

Publish the environment tags used by the overlays:

```bash
docker tag docker.io/argoprojregistry/argo-workflows-demo-app:0.1.0 docker.io/argoprojregistry/argo-workflows-demo-app:dev
docker tag docker.io/argoprojregistry/argo-workflows-demo-app:0.1.0 docker.io/argoprojregistry/argo-workflows-demo-app:test
docker tag docker.io/argoprojregistry/argo-workflows-demo-app:0.1.0 docker.io/argoprojregistry/argo-workflows-demo-app:staging
docker tag docker.io/argoprojregistry/argo-workflows-demo-app:0.1.0 docker.io/argoprojregistry/argo-workflows-demo-app:canary
docker tag docker.io/argoprojregistry/argo-workflows-demo-app:0.1.0 docker.io/argoprojregistry/argo-workflows-demo-app:green
docker push docker.io/argoprojregistry/argo-workflows-demo-app:dev
docker push docker.io/argoprojregistry/argo-workflows-demo-app:test
docker push docker.io/argoprojregistry/argo-workflows-demo-app:staging
docker push docker.io/argoprojregistry/argo-workflows-demo-app:canary
docker push docker.io/argoprojregistry/argo-workflows-demo-app:green
```

## First manual deployment checks

Render and inspect an overlay:

```bash
bash scripts/render-kustomize.sh test
```

Deploy to the test namespace:

```bash
kubectl apply -k k8s/overlays/test
kubectl rollout status deployment/myapp -n test
```

Smoke test the service:

```bash
kubectl port-forward svc/myapp 8080:80 -n test
```

In another shell:

```bash
curl http://127.0.0.1:8080/
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/api/catalog
curl 'http://127.0.0.1:8080/api/search?q=backend'
```

## How to map workflows to this repo

- CI or validation workflows should run `pytest`, `npm run test:ci`, Kustomize rendering and `conftest`.
- Test deployment workflows should target `k8s/overlays/test`.
- Staging validation workflows should target `k8s/overlays/staging`.
- Progressive delivery workflows should use `k8s/overlays/prod` and `k8s/overlays/canary`.
- Blue/green workflows should use `k8s/overlays/prod` and `k8s/overlays/green`.
- Rollback workflows should re-apply the previous stable image tag in `production`.

## What to prepare before the VM exists

- Pick the Ubuntu version: 22.04 LTS or 24.04 LTS.
- Pick the Kubernetes distribution: this guide assumes `k3s`.
- Pick the container registry you will actually use.
- Decide whether Argo will live in `argo` or another namespace.
- Verify that your workflow library expects the same deployment namespaces: `dev`, `test`, `staging`, `production`.
- List any additional dependencies needed by non-HTTP workflows, especially PostgreSQL, PVCs or secrets.

## Known limits

- The database-related templates still need a real PostgreSQL service and backup storage.
- The repo does not install Argo Events, ingress or certificate management; add those only if your workflow library requires them.
- This environment is intentionally small and optimized for workflow validation rather than production hardening.