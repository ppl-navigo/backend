from fastapi import FastAPI
from app.routers import health_check, file_downloader, file_streamer, file_uploader, analyze
from app.routers.legal_docs_generator import deepseek, legal_docs
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(health_check.router)
app.include_router(file_downloader.router)
app.include_router(file_streamer.router)
app.include_router(file_uploader.router)
app.include_router(deepseek.router)
app.include_router(legal_docs.router)
app.include_router(analyze.router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO : Remove this for nonstaging env
    allow_credentials=True,
    allow_methods=["*"],  # Izinkan semua metode (GET, POST, dll.)
    allow_headers=["*"],  # Izinkan semua header
)


@app.get("/")
async def root():
    return {"message": "MoU Analyzer is running"}