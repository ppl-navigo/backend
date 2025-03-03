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
    if data.system_prompt == "":
        raise HTTPException(status_code=422, detail="System prompt field required valid string")
    if data.query == "":
        raise HTTPException(status_code=422, detail="Query field required valid string")
    if data.temperature and (data.temperature < 0 or data.temperature > 1):
        raise HTTPException(status_code=422, detail="Temperature value is not a valid float, must be between 0 and 1")
    return StreamingResponse(deepseek_stream_response(data.system_prompt, data.query), media_type="text/plain")