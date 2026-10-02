# Architecture & DevOps Lifecycle

```
Developer -> feature branch -> PR -> CI (GitHub Actions)
   CI: flake8 -> pytest+coverage -> Bandit/pip-audit/gitleaks -> Docker build -> Trivy -> push to GHCR
   CD: develop -> staging (rolling) | main -> production (blue-green, approval gate)
Runtime (Kubernetes): Ingress -> Service -> Deployment (3 pods, HPA, PDB) -> PostgreSQL StatefulSet
Observability: /metrics -> Prometheus -> Grafana | JSON stdout logs -> Promtail -> Loki -> Grafana
```

| Requirement | Implementation |
|---|---|
| Course/student/content app | FastAPI + SQLAlchemy (`app/`) |
| Git branching | `docs/GIT_WORKFLOW.md` |
| Automated testing | `tests/` (pytest, 80% coverage gate) |
| CI | `.github/workflows/ci.yml` |
| Artifact repository | GitHub Container Registry (GHCR), tagged by commit SHA |
| Docker | Multi-stage non-root `Dockerfile`, `docker-compose.yml` |
| Kubernetes | `k8s/base` (probes, limits, HPA, PDB, securityContext) |
| Deployment strategy | Rolling (staging) and Blue-Green (prod) with rollback script |
| Monitoring | Prometheus + Grafana + alert rules (`monitoring/`) |
| Logging | Structured JSON logs -> Promtail -> Loki |
| Security scanning | Bandit (SAST), pip-audit (deps), gitleaks (secrets), Trivy (image + IaC), CodeQL |

## Prometheus on Kubernetes
Install kube-prometheus-stack via Helm and add a ServiceMonitor, or use the scrape annotations on the pod template.
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack -n monitoring
```

## Useful Grafana queries
- Request rate: `sum(rate(http_requests_total[1m])) by (path)`
- Error rate: `sum(rate(http_requests_total{status=~"5.."}[5m]))`
- p95 latency: `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))`
- Logs (Loki): `{container="learning-platform-app-1"} | json | status >= 500`
