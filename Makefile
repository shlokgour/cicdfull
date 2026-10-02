.PHONY: install test lint scan run up down kind
install: ; pip install -r requirements-dev.txt
lint:    ; flake8 app tests --max-line-length=100
test:    ; pytest --cov=app --cov-fail-under=80
scan:    ; bandit -r app -ll && pip-audit -r requirements.txt
run:     ; uvicorn app.main:app --reload
up:      ; docker compose up --build -d
down:    ; docker compose down -v
kind:    ; ./scripts/kind-setup.sh
