from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.routers.legal_docs_generator.dtos import DeepSeekRequest
import ollama

router = APIRouter()

async def deepseek_stream_response(system_prompt: str, query: str):
    """
    Streams responses from a locally deployed DeepSeek API through ollama.
    """
 
    stream = ollama.chat(
        model='deepseek-r1:8b',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': query}
        ],
        stream=True
    )

    for chunk in stream:
        yield chunk['message']['content']

@router.post("/deepseek", response_class=StreamingResponse)
async def deepseek_generate(data: DeepSeekRequest):
    return StreamingResponse(deepseek_stream_response(data.system_prompt, data.query), media_type="text/plain")