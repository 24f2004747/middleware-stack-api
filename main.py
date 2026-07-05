from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import time

app = FastAPI()

EMAIL = "24f2004747@ds.study.iitm.ac.in"

RATE_LIMIT = 10
WINDOW = 10

clients = {}

# Request ID middleware
@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ADD CORS AFTER CUSTOM MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app-e8g7ew.example.com",
        "https://exam.sanand.workers.dev",
    ],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/ping")
async def ping(request: Request):
    client = request.headers.get("X-Client-Id", "default")

    now = time.time()

    timestamps = [
        t for t in clients.get(client, [])
        if now - t < WINDOW
    ]

    if len(timestamps) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
        )

    timestamps.append(now)
    clients[client] = timestamps

    return {
        "email": EMAIL,
        "request_id": request.state.request_id,
    }
