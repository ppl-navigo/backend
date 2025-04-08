from fastapi import APIRouter, Response
from prometheus_client import generate_latest

router = APIRouter()

@router.get("/metrics")
def metrics():
    return Response(generate_latest())