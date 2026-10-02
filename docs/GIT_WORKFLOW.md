# Git Branching Strategy (GitFlow-lite)

| Branch | Purpose | Deploys to |
|---|---|---|
| `main` | Production-ready, tagged releases | Production (blue-green) |
| `develop` | Integration branch | Staging (rolling update) |
| `feature/<name>` | New work, branched from `develop` | CI only |
| `release/x.y.z` | Stabilisation before release | CI only |
| `hotfix/<name>` | Urgent prod fix, branched from `main` | CI only |

## Flow
1. `git checkout develop && git pull && git checkout -b feature/add-quizzes`
2. Commit using Conventional Commits: `feat: add quiz content type`, `fix: ...`, `chore: ...`
3. Open a PR to `develop`: CI (lint, tests, security scan, image build + Trivy) must pass, 1 review required.
4. Merge (squash). CD deploys `develop` to staging.
5. `git checkout -b release/1.1.0 develop` -> fix only bugs -> PR to `main`.
6. Merge to `main`, then `git tag v1.1.0 && git push --tags`. CD deploys to production (manual approval).
7. Merge `main` back into `develop`.

## Branch protection (Settings -> Branches)
- Require PR + 1 approval, require status checks: `test`, `security-scan`, `build-and-push`
- Disallow force-push on `main` and `develop`
- Require linear history

## Initial setup
```bash
git init && git add . && git commit -m "chore: initial commit"
git branch -M main && git checkout -b develop
git remote add origin git@github.com:<you>/learning-platform.git
git push -u origin main develop
```
