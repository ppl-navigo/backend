from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.routers.legal_docs_generator.dtos import LegalDocumentFormRequest
from app.routers.legal_docs_generator.deepseek import deepseek_stream_response
import httpx
import asyncio

router = APIRouter()

DEEPSEEK_API_URL = "http://localhost:8000/deepseek"  # Internal DeepSeek API URL

async def fetch_deepseek_response(request_data):
    """Send request to DeepSeek and stream the response"""
    async with httpx.AsyncClient() as client:
        try:
            async with client.stream("POST", DEEPSEEK_API_URL, json=request_data) as response:
                async for chunk in response.aiter_text():
                    yield chunk
                    await asyncio.sleep(0.05)  # Simulate network latency

        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"DeepSeek API request failed: {str(exc)}")

@router.post("/legal-docs-generator/generate", response_class=StreamingResponse)
async def generate_legal_document(data: LegalDocumentFormRequest):
    """Process user input and send request to DeepSeek"""
    empty_string_parameters = [
        data.judul == "", data.tujuan == "", len(data.pihak) == 0, data.mulai_kerja_sama == "", 
        data.akhir_kerja_sama == "", len(data.hak_pihak) == 0, len(data.kewajiban_pihak) == 0, data.pemecah_masalah == ""
    ]
    if any(empty_string_parameters):
        raise HTTPException(status_code=422, detail="valid field required, not empty string")

    deepseek_payload = {
        "system_prompt": f"Generate a legal document titled '{data.judul}' for {', '.join(data.pihak)}",
        "query": data.tujuan
    }

    return StreamingResponse(fetch_deepseek_response(deepseek_payload), media_type="text/plain")