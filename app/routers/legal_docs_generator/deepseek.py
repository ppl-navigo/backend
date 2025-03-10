from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from app.routers.legal_docs_generator.dtos import DeepSeekRequest
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import ValidationError

import ollama
from google import genai
from google.genai import types

import os

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

async def deepseek_stream_response(system_prompt: str, query: str):
    """
    Streams responses from a locally deployed DeepSeek API through ollama.
    """
    # Gemini API Request
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    response = client.models.generate_content_stream(
        model="gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt
        ),
        contents=[query]
    )
    for chunk in response:
        yield chunk.text

 
    # Deepseek Ollama Implementation
    # stream = ollama.chat(
    #     model='deepseek-r1:8b',
    #     messages=[
    #         {'role': 'system', 'content': system_prompt},
    #         {'role': 'user', 'content': query}
    #     ],
    #     stream=True
    # )
    # for chunk in stream:
    #     yield chunk['message']['content']

@router.post("/deepseek", response_class=StreamingResponse)
@limiter.limit("5/minute")
async def deepseek_generate(request: Request):
    # HACK: slowapi.limiter only works with Request objects, pydantic validation done manually
    try:
        body = await request.json()
        validated_request = DeepSeekRequest(**body)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return StreamingResponse(deepseek_stream_response(validated_request.system_prompt, validated_request.query), media_type="text/plain")