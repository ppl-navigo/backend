from openai import OpenAI
from config.settings import settings  # Import secure settings

class AIClient:
    """Handles AI requests and responses for risk analysis."""

    @staticmethod
    def analyze_risk(text: str) -> str:
        """Sends extracted text to AI for risk analysis using Qwen on OpenRouter."""
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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",  # 🔐 Use secure API key
        )

        # Combine extracted text with the stored risk analysis prompt
        full_prompt = f"{settings.AI_RISK_ANALYSIS_PROMPT}\n\n{text}"

        try:
            response = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": settings.SITE_URL,  # Optional for OpenRouter rankings
                    "X-Title": settings.SITE_NAME,  # Optional for OpenRouter rankings
                },
                extra_body={},
                model="qwen/qwen2.5-vl-72b-instruct:free",  # ✅ Use Qwen LLM
                messages=[
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": full_prompt}]
                    }
                ],
            )

            ai_output = response.choices[0].message.content.strip()

            # Temporary hardcode karena API sedang error, dan self deployed API in progress
            # ai_output = settings.AI_OUTPUT

            return ai_output
        except Exception as e:
            return f"❌ Gagal menganalisis dokumen: {str(e)}"
