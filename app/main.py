import json
import logging
import os
import sys
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy import text

from . import models  # noqa: F401  (register tables)
from .database import Base, engine
from .routers import courses, students

APP_VERSION = os.getenv("APP_VERSION", "dev")


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key in ("method", "path", "status", "duration_ms"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload)


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), handlers=[handler], force=True)
log = logging.getLogger("learning-platform")

REQUESTS = Counter("http_requests_total", "HTTP requests", ["method", "path", "status"])
LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["method", "path"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    log.info("startup complete, version=%s", APP_VERSION)
    yield


app = FastAPI(title="Learning Platform", version=APP_VERSION, lifespan=lifespan)
app.include_router(courses.router)
app.include_router(students.router)


@app.middleware("http")
async def observe(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    route = request.scope.get("route")
    path = route.path if route else request.url.path
    REQUESTS.labels(request.method, path, response.status_code).inc()
    LATENCY.labels(request.method, path).observe(elapsed)
    log.info(
        "request",
        extra={"method": request.method, "path": request.url.path,
               "status": response.status_code, "duration_ms": round(elapsed * 1000, 2)},
    )
    return response


@app.get("/")
def root():
    return {"service": "learning-platform", "version": APP_VERSION}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return Response(status_code=503, content='{"status":"db-unavailable"}',
                        media_type="application/json")


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
