import os
import time
import random
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

START_TIME = time.time()

MODE = os.getenv("MODE", "stable")
APP_VERSION = os.getenv("APP_VERSION", "0.0.1")

chaos_state = {
    "slow_duration": 0,
    "error_rate": 0,
}

def uptime():
    return int(time.time() - START_TIME)

@app.middleware("http")
async def chaos_middleware(request: Request, call_next):
    if MODE == "canary":
        if chaos_state["slow_duration"] > 0:
            time.sleep(chaos_state["slow_duration"])

        if chaos_state["error_rate"] > 0:
            if random.random() < chaos_state["error_rate"]:
                return JSONResponse(status_code=500, content={"error": "chaos error triggered"})

    response = await call_next(request)

    if MODE == "canary":
        response.headers["X-Mode"] = "canary"

    return response


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
    return {"status": "ok", "uptime": uptime(), "mode": MODE}


@app.post("/chaos")
async def chaos(payload: dict):
    if MODE != "canary":
        return JSONResponse(status_code=403, content={"error": "chaos only allowed in canary mode"})

    mode = payload.get("mode")

    if mode == "slow":
        chaos_state["slow_duration"] = int(payload.get("duration", 1))
        return {"status": "slow enabled", "duration": chaos_state["slow_duration"]}

    if mode == "error":
        chaos_state["error_rate"] = float(payload.get("rate", 0.5))
        return {"status": "error enabled", "rate": chaos_state["error_rate"]}

    if mode == "recover":
        chaos_state["slow_duration"] = 0
        chaos_state["error_rate"] = 0
        return {"status": "recovered"}

    return JSONResponse(status_code=400, content={"error": "invalid chaos mode"})