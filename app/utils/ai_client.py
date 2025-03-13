from openai import OpenAI
from config.settings import settings  # Import secure settings

class AIClient:
    """Handles AI requests and responses for risk analysis."""

    @staticmethod
    def analyze_risk(text: str) -> str:
        """Sends extracted text to AI for risk analysis using Qwen on OpenRouter."""
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,  # 🔐 Use secure API key
        )

        # Hardcoded AI risk analysis prompt
        AI_RISK_ANALYSIS_PROMPT = (
            "Analisis dokumen berikut untuk mengidentifikasi klausul yang berpotensi berisiko bagi pihak kedua. Risiko mencakup, namun tidak terbatas pada:\n\n"
            "* Ketidakseimbangan hak dan kewajiban antara pihak pertama dan pihak kedua\n"
            "* Klausul pembatalan yang merugikan\n"
            "* Klausul pembayaran yang berpotensi memberatkan\n"
            "* Klausul tanggung jawab yang bisa menyebabkan kerugian sepihak\n"
            "* Klausul force majeure yang tidak melindungi kepentingan pihak kedua\n"
            "* Klausul ambigu atau multi-tafsir yang bisa disalahgunakan\n"
            "* Klausul lain yang dapat menyebabkan dampak hukum negatif bagi pihak kedua\n\n"
            "Format hasil yang diharapkan:\n"
            "Klausul \\{nomor\\}: \"\\{kalimat atau kata-kata berisiko\\}\". Alasan: \"\\{penjelasan mengapa klausul ini berisiko\\}\".\n\n"
            "Jika dokumen memiliki bahasa yang tidak dikenali, tampilkan pesan \"Bahasa tidak didukung\". "
            "Jika tidak ditemukan klausul berisiko, tampilkan pesan \"Tidak ditemukan klausul yang dapat dianalisis\". "
            "Jika terjadi kesalahan sistem, tampilkan pesan \"Gagal menganalisis dokumen, coba lagi nanti\".\n\n"
            "Setiap klausul yang ditandai harus memiliki minimal satu alasan mengapa klausul tersebut berisiko, "
            "tetapi jangan berikan rekomendasi perbaikan terlebih dahulu."
        )

        # Combine extracted text with the hardcoded prompt
        full_prompt = f"{AI_RISK_ANALYSIS_PROMPT}\n\n{text}"
        print(full_prompt)
        
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
            print(ai_output)
            # Temporary hardcode karena API sedang error, dan self deployed API in progress
            # ai_output = settings.AI_OUTPUT

            return ai_output
        except Exception as e:
            return f"❌ Gagal menganalisis dokumen: {str(e)}"
