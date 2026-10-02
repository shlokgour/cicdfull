# Learning Platform: Full DevOps Lifecycle

REST API for **courses, students and content** with a complete DevOps pipeline.

## Quick start
```bash
make install && make test      # tests + coverage
make run                       # http://localhost:8000/docs
make up                        # app + Postgres + Prometheus(9090) + Grafana(3000) + Loki
make kind                      # local Kubernetes via kind
```

## API
| Method | Path | Description |
|---|---|---|
| POST/GET | `/courses` | Create / list courses |
| GET/PUT/DELETE | `/courses/{id}` | Course detail |
| POST/GET | `/courses/{id}/contents` | Add / list content (text, video, pdf, quiz) |
| DELETE | `/courses/{id}/contents/{cid}` | Remove content |
| POST/GET | `/students` | Create / list students |
| POST | `/students/{sid}/enroll/{cid}` | Enroll student |
| GET | `/health`, `/ready`, `/metrics` | Probes and Prometheus metrics |

## Docs
- `docs/GIT_WORKFLOW.md` — branching strategy
- `docs/ARCHITECTURE.md` — pipeline, K8s, monitoring, security mapping

## Before first push
1. Replace `OWNER` in `k8s/**` with your GitHub username/org (lowercase).
2. Add repo secret `KUBE_CONFIG_B64` (base64 of kubeconfig) for CD.
3. Create `staging` and `production` environments (add required reviewers to production).
4. Replace demo secrets in `k8s/base/10-config-secret.yaml` with a real secret manager.
