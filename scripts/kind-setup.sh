#!/usr/bin/env bash
# Local cluster: build image, load into kind, deploy rolling manifests.
set -euo pipefail
kind create cluster --name lp 2>/dev/null || true
docker build -t learning-platform:local .
kind load docker-image learning-platform:local --name lp
kubectl apply -f k8s/base/00-namespace.yaml -f k8s/base/10-config-secret.yaml -f k8s/base/20-postgres.yaml
kubectl apply -f k8s/base/30-deployment.yaml
kubectl -n learning-platform set image deployment/learning-platform app=learning-platform:local
kubectl -n learning-platform rollout status deployment/learning-platform
echo "Run: kubectl -n learning-platform port-forward svc/learning-platform 8000:80"
