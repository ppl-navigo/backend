from fastapi import FastAPI
from app.routers import health_check, analyze
from app.routers.retrieval import search
from app.routers.metrics import autometrics
from app.routers.legal_docs_generator import deepseek, legal_docs
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator
from contextlib import asynccontextmanager
from app.config.graylog import logger

limiter = Limiter(key_func=get_remote_address)

instrumentator = Instrumentator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    instrumentator.expose(app)
    yield

app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def log_middleware(request, call_next):
    response = await call_next(request)
    logger.info(
        str(request.url),
        extra={
            "req": {"method": request.method, "url": str(request.url)},
            "res": {"status_code": response.status_code},
        },
    )
    return response

instrumentator.instrument(app)
instrumentator.expose(app)

# Include routers
app.include_router(health_check.router)
app.include_router(deepseek.router)
app.include_router(legal_docs.router)
app.include_router(analyze.router)
app.include_router(search.router)
app.include_router(autometrics.router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO : Remove this for nonstaging env
    allow_credentials=True,
    allow_methods=["*"],  # Izinkan semua metode (GET, POST, dll.)
    allow_headers=["*"],  # Izinkan semua header
)


print("Started")
@app.get("/")
async def root():
    return {"message": "MoU Analyzer is running"}