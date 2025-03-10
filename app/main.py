from fastapi import FastAPI
from app.routers import health_check
from app.routers.legal_docs_generator import deepseek, legal_docs
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(health_check.router)
app.include_router(deepseek.router)
app.include_router(legal_docs.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Bisa juga ["*"] untuk semua origin
    allow_credentials=True,
    allow_methods=["*"],  # Izinkan semua metode (GET, POST, dll.)
    allow_headers=["*"],  # Izinkan semua header
)

@app.get("/")
async def root():
    return {"message": "Hello World"}