from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import time

app = FastAPI()

EMAIL = "24f2004747@ds.study.iitm.ac.in"

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app-e8g7ew.example.com",
    ],
    # Allow the exam page origin (workers.dev)
    allow_origin_regex=r"https://.*\.workers\.dev",
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

RATE_LIMIT = 10
WINDOW = 10

client_requests = {}


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID")

    if not request_id:
        request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    # Never rate-limit preflight requests
    if request.method == "OPTIONS":
        return await call_next(request)

    client = request.headers.get("X-Client-Id", "default")

    now = time.time()

    bucket = client_requests.get(client, [])

    bucket = [t for t in bucket if now - t < WINDOW]

    if len(bucket) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
        )

    bucket.append(now)
    client_requests[client] = bucket

    return await call_next(request)


@app.get("/ping")
async def ping(request: Request):
    return {
        "email": EMAIL,
        "request_id": request.state.request_id,
    }
