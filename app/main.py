from fastapi import FastAPI
from app.routers import health_check
from app.routers.legal_docs_generator import deepseek, legal_docs

app = FastAPI()
app.include_router(health_check.router)
app.include_router(deepseek.router)
app.include_router(legal_docs.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}