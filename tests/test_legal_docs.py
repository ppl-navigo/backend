from fastapi.testclient import TestClient
import pytest
from app.main import app
import asyncio
from unittest.mock import patch

ROUTE = '/legal-docs-generator'
client = TestClient(app)

"""
Test below focus on the first acceptance criteria of PBI "Membuat Dokumen Legal":

Pengguna dapat mengisi dan mengunggah prompt penjelasan profil dokumen mereka melalui form yang disediakan. 
Jika prompt gagal diunggah, formatnya tidak sesuai, atau ada kesalahan teknis, sistem akan menampilkan 
pesan kesalahan yang jelas, memberikan petunjuk untuk memperbaiki prompt, dan meminta pengguna untuk 
mencoba mengunggah kembali dengan format yang sesuai.
"""


async def mock_deepseek_stream_response(request_data):
    """Mocked fetch_deepseek_response"""
    MOCKED_RESPONSE = "<think>\nAlright, I need to help the user create a Memorandum of Understanding (MoU) between Perusahaan A and Perusahaan B focused on their collaboration for an AI project. First, I should recall what an MoU typically includes.\n\nAn MoU is usually not legally binding but outlines the intention and terms"
    for word in MOCKED_RESPONSE.split():
        yield word + " "
        await asyncio.sleep(0.01)  # Simulate streaming delay


@patch("app.routers.legal_docs_generator.legal_docs.fetch_deepseek_response")
@pytest.mark.asyncio
async def test_streaming_legal_document_success(mock_deepseek):
    """✅ Should successfully stream a legal document generation"""
    mock_deepseek.side_effect = mock_deepseek_stream_response
    # mock_deepseek.stop()

    document_data = {
        "jenis_kontrak": "Perjanjian Kerjasama",
        "judul": "Kontrak Kemitraan Strategis",
        "tujuan": "Menjalin kemitraan strategis antara dua perusahaan",
        "pihak": [
            {
                "nama": "PT ABC",
                "hak_pihak": ["Menggunakan teknologi eksklusif", "Menerima laporan keuangan"],
                "kewajiban_pihak": ["Membayar biaya lisensi", "Memberikan dukungan teknis"]
            },
            {
                "nama": "PT XYZ",
                "hak_pihak": ["Menerima pembayaran royalti", "Mengakses laporan tahunan"],
                "kewajiban_pihak": ["Menyediakan akses teknologi", "Memberikan pelatihan kepada tim"]
            }
        ],
        "mulai_kerja_sama": "2025-04-01",
        "akhir_kerja_sama": "2028-04-01",
        "pemecah_masalah": "Arbitrase Internasional",
        "comment": "Kesepakatan perlu direvisi setiap tahun",
        "author": "email@example.com"
    }

    with client.stream("POST", f"{ROUTE}/generate", json=document_data) as response:
        assert response.status_code == 200

        chunks = []
        for chunk in response.iter_text():
            chunks.append(chunk)
            assert len(chunk) > 0, chunks  # Ensure token-by-token output


@patch("app.routers.legal_docs_generator.legal_docs.fetch_deepseek_response")
@pytest.mark.asyncio
async def test_submit_legal_document_success(mock_deepseek):
    """✅ Should successfully generate a legal document"""
    mock_deepseek.side_effect = mock_deepseek_stream_response

    document_data = {
        "jenis_kontrak": "Perjanjian Kerjasama",
        "judul": "Kontrak Kemitraan Strategis",
        "tujuan": "Menjalin kemitraan strategis antara dua perusahaan",
        "pihak": [
            {
                "nama": "PT ABC",
                "hak_pihak": ["Menggunakan teknologi eksklusif", "Menerima laporan keuangan"],
                "kewajiban_pihak": ["Membayar biaya lisensi", "Memberikan dukungan teknis"]
            },
            {
                "nama": "PT XYZ",
                "hak_pihak": ["Menerima pembayaran royalti", "Mengakses laporan tahunan"],
                "kewajiban_pihak": ["Menyediakan akses teknologi", "Memberikan pelatihan kepada tim"]
            }
        ],
        "mulai_kerja_sama": "2025-04-01",
        "akhir_kerja_sama": "2028-04-01",
        "pemecah_masalah": "Arbitrase Internasional",
        "author": "email@example.com"  # without comment parameter should be fine
    }
    response = client.post(f"{ROUTE}/generate", json=document_data)

    assert response.status_code == 200
    assert len(response.text) > 0  # Ensure generated document is not empty


@patch("app.routers.legal_docs_generator.legal_docs.fetch_deepseek_response")
@pytest.mark.asyncio
async def test_submit_legal_document_invalid_email(mock_deepseek):
    """❌ Should fail due to invalid email format"""
    mock_deepseek.side_effect = mock_deepseek_stream_response

    document_data = {
        "jenis_kontrak": "Perjanjian Kerjasama",
        "judul": "Kontrak Kemitraan Strategis",
        "tujuan": "Menjalin kemitraan strategis antara dua perusahaan",
        "pihak": [
            {
                "nama": "PT ABC",
                "hak_pihak": ["Menggunakan teknologi eksklusif", "Menerima laporan keuangan"],
                "kewajiban_pihak": ["Membayar biaya lisensi", "Memberikan dukungan teknis"]
            },
            {
                "nama": "PT XYZ",
                "hak_pihak": ["Menerima pembayaran royalti", "Mengakses laporan tahunan"],
                "kewajiban_pihak": ["Menyediakan akses teknologi", "Memberikan pelatihan kepada tim"]
            }
        ],
        "mulai_kerja_sama": "2025-04-01",
        "akhir_kerja_sama": "2028-04-01",
        "pemecah_masalah": "Arbitrase Internasional",
        "comment": "",
        "author": "invalid_email"
    }
    response = client.post(f"{ROUTE}/generate", json=document_data)

    assert response.status_code == 422
    # failed case, unprocessable entity
    assert "value is not a valid email" in response.text


@patch("app.routers.legal_docs_generator.legal_docs.fetch_deepseek_response")
@pytest.mark.asyncio
async def test_submit_legal_document_missing_fields(mock_deepseek):
    """❌ Should fail due to missing fields"""
    mock_deepseek.side_effect = mock_deepseek_stream_response

    response = client.post(f"{ROUTE}/generate", json={})

    assert response.status_code == 422
    # failed case, unprocessable entity
    assert "field required" in response.text.lower()


@patch("app.routers.legal_docs_generator.legal_docs.fetch_deepseek_response")
@pytest.mark.asyncio
async def test_generate_legal_doc_empty_fields(mock_deepseek):
    """❌ Should fail when all fields are empty"""
    mock_deepseek.side_effect = mock_deepseek_stream_response

    document_data = {
        "jenis_kontrak": "",
        "judul": "",
        "tujuan": "",
        "pihak": [],
        "mulai_kerja_sama": "",
        "akhir_kerja_sama": "",
        "pemecah_masalah": "",
        "comment": "",
        "author": ""
    }
    response = client.post(f"{ROUTE}/generate", json=document_data)

    assert response.status_code == 422  # corner case, unprocessable entity


@patch("app.routers.legal_docs_generator.legal_docs.fetch_deepseek_response")
@pytest.mark.asyncio
async def test_generate_legal_doc_missing_judul(mock_deepseek):
    """❌ Should fail when 'judul' field is missing"""
    mock_deepseek.side_effect = mock_deepseek_stream_response

    document_data = {
        "jenis_kontrak": "Perjanjian Kerjasama",
        # "judul": "Kontrak Kemitraan Strategis", # missing judul
        "tujuan": "Menjalin kemitraan strategis antara dua perusahaan",
        "pihak": [
            {
                "nama": "PT ABC",
                "hak_pihak": ["Menggunakan teknologi eksklusif", "Menerima laporan keuangan"],
                "kewajiban_pihak": ["Membayar biaya lisensi", "Memberikan dukungan teknis"]
            },
            {
                "nama": "PT XYZ",
                "hak_pihak": ["Menerima pembayaran royalti", "Mengakses laporan tahunan"],
                "kewajiban_pihak": ["Menyediakan akses teknologi", "Memberikan pelatihan kepada tim"]
            }
        ],
        "mulai_kerja_sama": "2025-04-01",
        "akhir_kerja_sama": "2028-04-01",
        "pemecah_masalah": "Arbitrase Internasional",
        "comment": "Kesepakatan perlu direvisi setiap tahun",
        "author": "email@example.com"
    }
    response = client.post(f"{ROUTE}/generate", json=document_data)

    assert response.status_code == 422
    assert "field" in response.text.lower(
    ) and "required" in response.text.lower()  # failed case, bad request
