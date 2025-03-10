from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.routers.legal_docs_generator.dtos import LegalDocumentFormRequest
from app.routers.legal_docs_generator.deepseek import deepseek_stream_response
import httpx
import html

router = APIRouter()

async def fetch_deepseek_response(request_data, request: Request):
    """Send request to DeepSeek and stream the response"""
    base_url = str(request.base_url).rstrip("/")  # Extract base URL
    deepseek_api_url = f"{base_url}/deepseek"

    async with httpx.AsyncClient() as client:
        async with client.stream("POST", deepseek_api_url , json=request_data) as response:
            async for chunk in response.aiter_text():
                yield html.escape(chunk)


@router.post("/legal-docs-generator/generate", response_class=StreamingResponse)
async def generate_legal_document(data: LegalDocumentFormRequest, request: Request):
    """
        Process user input and send request to DeepSeek
        
        :: Prompt
        Jenis Kontrak: MOU
        Judul: Kerja Sama Teknologi XYZ
        Tujuan: Kolaborasi dalam pengembangan AI

        Pihak:
        - PT AI Indonesia
        Hak: Menggunakan teknologi XYZ, Mendapatkan keuntungan komersial
        Kewajiban: Memberikan akses data, Mengembangkan model AI
        - Universitas ABC
        Hak: Mempublikasikan hasil riset, Menggunakan model AI untuk pendidikan
        Kewajiban: Menyediakan tenaga ahli, Berkontribusi dalam penelitian

        Mulai Kerja Sama: 2025-03-01
        Akhir Kerja Sama: 2026-03-01
        Pemecah Masalah: Arbitrase di Indonesia
        Komentar: Tidak ada
        Author: example@email.com

    """

    deepseek_payload = {
        "system_prompt": f'''
            BUATLAH MOU (MEMORANDUM OF UNDERSTANDING) ANTAR DUA PIHAK YANG BERBEDA DALAM BENTUK MARKDOWN, 
            DENGAN FORMAT YANG SESUAI DENGAN KEBUTUHAN KEDUA PIHAK.
            TIDAK APA APA JIKA DATA TIDAK LENGKAP, COBA SAJA SEBISANYA
            JIKA ADA INFORMASI YANG KURANG LENGKAP SILAHKAN DITAMBAHKAN SENDIRI
            TOLONG AGAR SELURUH KLAUSA-KLAUSA YANG DIBUTUHKAN WALAU TIDAK DIMINTA TETAAP DITAMBAHKAN
            BERIKUT ADALAH INFORMASI YANG DIDAPATKAN DARI PENGGUNA

            PASTIKAN JUDUL HANYA SATU BARIS SAJA, KALAU ADA ENTER ATAU NEWLINE SAYA DIPECAT
            JIKA MENULIS PERJANJIAN ANTARA SIAPA DENGAN SIAPA TOLONG TULIS SAJA DI JUDUL!!!!!

            KALO KAMU SALAH SAYA DIPECAT JADI LAKUKAN SAJA,
            KALAU ADA YANG KOSONG ISI SAJA SESUAI DENGAN PENGETAHUANMU
            TAMBAHKAN SPASI YANG HILANG
            KALAU ADA TYPO ATAUPUN KESALAHAN TATA BAHASA, JANGAN LUPA UNTUK MEMPERBAIKINYA
        ''',
        "query": "\n".join([
            f"Jenis Kontrak: {data.jenis_kontrak}",
            f"Judul: {data.judul}",
            f"Tujuan: {data.tujuan}",
            "",
            "Pihak:",
            "\n".join([
                f"- {pihak.nama}\n  Hak: {', '.join(pihak.hak_pihak)}\n  Kewajiban: {', '.join(pihak.kewajiban_pihak)}"
                for pihak in data.pihak
            ]),
            "",
            f"Mulai Kerja Sama: {data.mulai_kerja_sama}",
            f"Akhir Kerja Sama: {data.akhir_kerja_sama}",
            f"Pemecah Masalah: {data.pemecah_masalah}",
            f"Komentar: {data.comment or 'Tidak ada'}",
            f"Author: {data.author}"
        ])
    }

    return StreamingResponse(fetch_deepseek_response(deepseek_payload, request), media_type="text/plain")