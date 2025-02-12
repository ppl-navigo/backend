from fastapi import FastAPI
from app.routers import health_check

app = FastAPI()
app.include_router(health_check.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}