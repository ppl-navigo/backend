from fastapi import FastAPI
from app.routers import health_check

app = FastAPI()
app.include_router(health_check.router)

def db_conn():
    pass

@app.get("/")
async def root():
    return {"message": "Hello World"}