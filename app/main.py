import os
import time
import random
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

START_TIME = time.time()

MODE = os.getenv("MODE", "stable")
APP_VERSION = os.getenv("APP_VERSION", "0.0.1")

# -----------------------------
# CHAOS STATE
# -----------------------------
chaos_state = {
    "slow_duration": 0,
    "error_rate": 0,
}

def uptime_seconds():
    return int(time.time() - START_TIME)

def chaos_active_value():
    """
    chaos_active:
      0 = none
      1 = slow
      2 = error
    """
    if chaos_state["error_rate"] > 0:
        return 2
    if chaos_state["slow_duration"] > 0:
        return 1
    return 0

# -----------------------------
# PROMETHEUS METRICS
# -----------------------------
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)

APP_UPTIME = Gauge(
    "app_uptime_seconds",
    "Application uptime in seconds"
)

APP_MODE = Gauge(
    "app_mode",
    "Application mode (stable=0, canary=1)"
)

CHAOS_ACTIVE = Gauge(
    "chaos_active",
    "Chaos state (0=none, 1=slow, 2=error)"
)

# Set mode gauge once at startup
if MODE == "canary":
    APP_MODE.set(1)
else:
    APP_MODE.set(0)


# -----------------------------
# MIDDLEWARE (Chaos + Metrics)
# -----------------------------
@app.middleware("http")
async def chaos_and_metrics_middleware(request: Request, call_next):
    path = request.url.path
    method = request.method

    start = time.time()

    # Apply chaos only in canary mode
    if MODE == "canary":
        if chaos_state["slow_duration"] > 0:
            time.sleep(chaos_state["slow_duration"])

        if chaos_state["error_rate"] > 0:
            if random.random() < chaos_state["error_rate"]:
                status_code = "500"
                HTTP_REQUESTS_TOTAL.labels(method=method, path=path, status_code=status_code).inc()
                HTTP_REQUEST_DURATION.labels(method=method, path=path).observe(time.time() - start)

                return JSONResponse(
                    status_code=500,
                    content={"error": "chaos error triggered"}
                )

    response = await call_next(request)

    # Add canary header if in canary mode
    if MODE == "canary":
        response.headers["X-Mode"] = "canary"

    # Metrics update
    status_code = str(response.status_code)
    HTTP_REQUESTS_TOTAL.labels(method=method, path=path, status_code=status_code).inc()
    HTTP_REQUEST_DURATION.labels(method=method, path=path).observe(time.time() - start)

    # Update gauges
    APP_UPTIME.set(uptime_seconds())
    CHAOS_ACTIVE.set(chaos_active_value())

    return response


# -----------------------------
# ROUTES
# -----------------------------
@app.get("/")
def root():
    return {
        "message": "Welcome to SwiftDeploy API",
        "mode": MODE,
        "version": APP_VERSION,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
    }


@app.get("/healthz")
def healthz():
    # Update gauges whenever health is called
    APP_UPTIME.set(uptime_seconds())
    CHAOS_ACTIVE.set(chaos_active_value())

    return {"status": "ok", "uptime": uptime_seconds(), "mode": MODE}


@app.post("/chaos")
async def chaos(payload: dict):
    if MODE != "canary":
        return JSONResponse(
            status_code=403,
            content={"error": "chaos only allowed in canary mode"}
        )

    mode = payload.get("mode")

    if mode == "slow":
        chaos_state["slow_duration"] = int(payload.get("duration", 1))
        CHAOS_ACTIVE.set(chaos_active_value())
        return {"status": "slow enabled", "duration": chaos_state["slow_duration"]}

    if mode == "error":
        chaos_state["error_rate"] = float(payload.get("rate", 0.5))
        CHAOS_ACTIVE.set(chaos_active_value())
        return {"status": "error enabled", "rate": chaos_state["error_rate"]}

    if mode == "recover":
        chaos_state["slow_duration"] = 0
        chaos_state["error_rate"] = 0
        CHAOS_ACTIVE.set(chaos_active_value())
        return {"status": "recovered"}

    return JSONResponse(status_code=400, content={"error": "invalid chaos mode"})


@app.get("/metrics")
def metrics():
    # Ensure gauges are always fresh
    APP_UPTIME.set(uptime_seconds())
    CHAOS_ACTIVE.set(chaos_active_value())

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)