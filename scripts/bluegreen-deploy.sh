#!/usr/bin/env bash
# Blue-green release: deploy to the idle slot, verify, switch traffic, keep old slot for rollback.
# Usage: IMAGE=ghcr.io/owner/learning-platform:<sha> ./scripts/bluegreen-deploy.sh
set -euo pipefail
NS=learning-platform
: "${IMAGE:?set IMAGE}"

kubectl apply -f k8s/base/00-namespace.yaml -f k8s/base/10-config-secret.yaml -f k8s/base/20-postgres.yaml
kubectl apply -f k8s/bluegreen/

LIVE=$(kubectl -n $NS get svc lp-live -o jsonpath='{.spec.selector.slot}')
if [ "$LIVE" = "blue" ]; then IDLE=green; else IDLE=blue; fi
echo "Live: $LIVE  ->  deploying to idle: $IDLE"

kubectl -n $NS set image deployment/lp-$IDLE app="$IMAGE"
kubectl -n $NS rollout status deployment/lp-$IDLE --timeout=180s

# Smoke test the idle slot through a temporary pod
kubectl -n $NS run smoke-$RANDOM --rm -i --restart=Never --image=curlimages/curl:8.10.1 -- \
  curl -fsS "http://lp-$IDLE/ready" >/dev/null
echo "Smoke test passed"

kubectl -n $NS patch svc lp-live -p "{\"spec\":{\"selector\":{\"app\":\"lp\",\"slot\":\"$IDLE\"}}}"
echo "Traffic switched to $IDLE. Previous slot ($LIVE) kept for rollback: ./scripts/rollback.sh"
