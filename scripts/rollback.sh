#!/usr/bin/env bash
# Instant rollback: point the live Service back at the previous slot.
set -euo pipefail
NS=learning-platform
LIVE=$(kubectl -n $NS get svc lp-live -o jsonpath='{.spec.selector.slot}')
if [ "$LIVE" = "blue" ]; then PREV=green; else PREV=blue; fi
kubectl -n $NS patch svc lp-live -p "{\"spec\":{\"selector\":{\"app\":\"lp\",\"slot\":\"$PREV\"}}}"
echo "Rolled back: live slot is now $PREV"
