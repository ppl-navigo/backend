from fastapi import FastAPI
from app.routers import health_check, file_uploader

app = FastAPI()
app.include_router(health_check.router)
app.include_router(file_uploader.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}