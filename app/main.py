from fastapi import FastAPI
from app.routers import health_check
from app.routers.legal_docs_generator import deepseek, legal_docs
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(health_check.router)
app.include_router(deepseek.router)
app.include_router(legal_docs.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}