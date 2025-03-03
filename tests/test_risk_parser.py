import pytest
import logging
from unittest.mock import patch
from app.utils.risk_parser import RiskParser

logger = logging.getLogger(__name__)

# ==========================
# Positive Cases
# ==========================

@pytest.fixture
def sample_ai_response():
    """Mock AI response with multiple risk clauses."""
    return '''
    Klausul 2: "Jasa dari PIHAK PERTAMA kepada PIHAK KEDUA dimulai sejak PIHAK KEDUA melakukan PEMBAYARAN."
    Alasan: "Tidak ada perlindungan bagi PIHAK KEDUA terhadap keterlambatan PIHAK PERTAMA."

    Klausul 6: "Tahap pertama sebagai uang muka sebesar Rp. ______________ akan dibayarkan oleh PIHAK KEDUA."
    Alasan: "Tidak ada jaminan bahwa PIHAK PERTAMA akan menyelesaikan pekerjaan sesuai standar."
    '''

def test_parse_ai_risk_analysis_valid_response(sample_ai_response):
    """✅ Test parsing a valid AI-generated response with multiple clauses."""
    parsed_data = RiskParser.parse_ai_risk_analysis(sample_ai_response)

    expected_output = [
        {
            "clause": "Klausul 2",
            "risky_text": "Jasa dari PIHAK PERTAMA kepada PIHAK KEDUA dimulai sejak PIHAK KEDUA melakukan PEMBAYARAN.",
            "reason": "Tidak ada perlindungan bagi PIHAK KEDUA terhadap keterlambatan PIHAK PERTAMA."
        },
        {
            "clause": "Klausul 6",
            "risky_text": "Tahap pertama sebagai uang muka sebesar Rp. ______________ akan dibayarkan oleh PIHAK KEDUA.",
            "reason": "Tidak ada jaminan bahwa PIHAK PERTAMA akan menyelesaikan pekerjaan sesuai standar."
        }
    ]

    assert parsed_data == expected_output, f"Unexpected output: {parsed_data}"

# ==========================
# Negative Cases
# ==========================

def test_parse_ai_risk_analysis_empty_response():
    """❌ Test parsing an empty AI response."""
    ai_response = ""
    parsed_data = RiskParser.parse_ai_risk_analysis(ai_response)

    assert parsed_data[0]["clause"] == "N/A"
    assert parsed_data[0]["risky_text"] == "Tidak ditemukan klausul yang dapat dianalisis"
    assert parsed_data[0]["reason"] == "Dokumen aman atau tidak dikenali"

def test_parse_ai_risk_analysis_no_valid_clauses():
    """❌ Test when no valid risk clauses are present in the response."""
    ai_response = "Dokumen ini aman dan tidak memiliki klausul berisiko."
    
    parsed_data = RiskParser.parse_ai_risk_analysis(ai_response)

    assert parsed_data[0]["clause"] == "N/A"
    assert parsed_data[0]["risky_text"] == "Tidak ditemukan klausul yang dapat dianalisis"
    assert parsed_data[0]["reason"] == "Dokumen aman atau tidak dikenali"

def test_parse_ai_risk_analysis_invalid_format():
    """❌ Test when the AI response format is incorrect or incomplete."""
    ai_response = "Klausul 3: Tidak lengkap"
    
    parsed_data = RiskParser.parse_ai_risk_analysis(ai_response)

    assert parsed_data[0]["clause"] == "N/A"
    assert parsed_data[0]["risky_text"] == "Tidak ditemukan klausul yang dapat dianalisis"
    assert parsed_data[0]["reason"] == "Dokumen aman atau tidak dikenali"

# ==========================
# Performance & Scaling Tests
# ==========================

def test_parse_ai_risk_analysis_large_input(benchmark):
    """✅ Test parsing a large AI response to ensure performance holds up."""
    ai_response = "\n".join([
        f'Klausul {i}: "Klausul contoh {i}". Alasan: "Alasan contoh {i}."' for i in range(1, 51)
    ])
    
    parsed_data = benchmark(RiskParser.parse_ai_risk_analysis, ai_response)

    assert len(parsed_data) == 50, f"Expected 50 clauses, but got {len(parsed_data)}"
    assert parsed_data[0]["clause"] == "Klausul 1"
    assert parsed_data[-1]["clause"] == "Klausul 50"

# ==========================
# Error Handling Tests
# ==========================

def test_parse_ai_risk_analysis_invalid_regex():
    """❌ Test unexpected input formats with unstructured data."""
    ai_response = "Ini bukan format yang dikenali dan tidak memiliki klausul yang bisa diidentifikasi."

    parsed_data = RiskParser.parse_ai_risk_analysis(ai_response)

    assert parsed_data[0]["clause"] == "N/A"
    assert parsed_data[0]["risky_text"] == "Tidak ditemukan klausul yang dapat dianalisis"
    assert parsed_data[0]["reason"] == "Dokumen aman atau tidak dikenali"

def test_parse_ai_risk_analysis_logging(caplog):
    """✅ Ensure logging messages are generated correctly."""
    ai_response = 'Klausul 1: "Tes klausul." Alasan: "Tes alasan."'

    with caplog.at_level(logging.INFO):
        RiskParser.parse_ai_risk_analysis(ai_response)

    # Now standard logging messages are captured by caplog
    assert any("Parsing AI risk analysis response" in r.message for r in caplog.records), "No parsing log found"
    assert any("Successfully parsed AI risk analysis" in r.message for r in caplog.records), "No success log found"

def test_parse_ai_risk_analysis_unexpected_error(caplog):
    """❌ Test handling of unexpected errors in AI response parsing."""
    ai_response = 'Klausul 1: "Tes klausul." Alasan: "Tes alasan."'

    # Simulate an unexpected exception inside the `try` block
    with patch("re.findall", side_effect=Exception("Unexpected regex error")):
        with caplog.at_level(logging.ERROR):
            parsed_data = RiskParser.parse_ai_risk_analysis(ai_response)

    # Verify the error is logged
    assert any("Error while parsing AI risk analysis: Unexpected regex error" in r.message for r in caplog.records), "Expected error log not found"

    # Verify fallback response
    assert parsed_data[0]["clause"] == "N/A"
    assert parsed_data[0]["risky_text"] == "Parsing gagal"
    assert parsed_data[0]["reason"] == "Kesalahan sistem saat mengolah dokumen"