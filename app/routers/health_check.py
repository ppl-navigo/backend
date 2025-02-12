from fastapi import APIRouter

router = APIRouter()

@router.get("/health_check", tags=["health_check"])
async def health_check():
    return {"status": "server is healthy"}