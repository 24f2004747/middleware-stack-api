from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import time

app = FastAPI()

EMAIL = "24f2004747@ds.study.iitm.ac.in"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app-e8g7ew.example.com",
        "https://exam.sanand.workers.dev",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

RATE_LIMIT = 10
WINDOW = 10
rate_limit_store = {}

@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_id = request.headers.get("X-Client-Id", "default")
    now = time.time()
    timestamps = [t for t in rate_limit_store.get(client_id, []) if now - t < WINDOW]
    if len(timestamps) >= RATE_LIMIT:
        return JSONResponse(status_code=429, content={"detail":"Rate limit exceeded"})
    timestamps.append(now)
    rate_limit_store[client_id] = timestamps
    return await call_next(request)

@app.get("/ping")
async def ping(request: Request):
    return {
        "email": EMAIL,
        "request_id": request.state.request_id,
    }
