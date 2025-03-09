from fastapi import FastAPI
from app.routers import health_check, file_downloader, file_streamer
from app.routers import analyze, health_check

app = FastAPI()

app.include_router(analyze.router)
app.include_router(health_check.router)
app.include_router(file_downloader.router)
app.include_router(file_streamer.router)

@app.get("/")
async def root():
    return {"message": "MoU Analyzer is running"}