import pytest
from app.utils.risk_parser import parse_ai_risk_analysis

# ==========================
# Positive Cases
# ==========================

def test_parse_ai_risk_analysis_valid_response():
    """✅ Test parsing a valid AI-generated response with multiple clauses."""
    ai_response = '''
    Klausul 2: "Jasa dari PIHAK PERTAMA kepada PIHAK KEDUA dimulai sejak PIHAK KEDUA melakukan PEMBAYARAN."
    Alasan: "Tidak ada perlindungan bagi PIHAK KEDUA terhadap keterlambatan PIHAK PERTAMA."
    
    Klausul 6: "Tahap pertama sebagai uang muka sebesar Rp. ______________ akan dibayarkan oleh PIHAK KEDUA."
    Alasan: "Tidak ada jaminan bahwa PIHAK PERTAMA akan menyelesaikan pekerjaan sesuai standar."
    '''
    
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

    parsed_data = parse_ai_risk_analysis(ai_response)
    assert parsed_data == expected_output, f"Unexpected output: {parsed_data}"

# ==========================
# Negative Cases
# ==========================

def test_parse_ai_risk_analysis_empty_response():
    """❌ Test parsing an empty AI response."""
    ai_response = ""
    expected_output = [
        {
            "clause": "N/A",
            "risky_text": "Tidak ditemukan klausul yang dapat dianalisis",
            "reason": "Dokumen aman atau tidak dikenali"
        }
    ]
    
    parsed_data = parse_ai_risk_analysis(ai_response)
    assert parsed_data == expected_output, f"Unexpected output: {parsed_data}"

def test_parse_ai_risk_analysis_no_valid_clauses():
    """❌ Test when no valid risk clauses are present in the response."""
    ai_response = "Dokumen ini aman dan tidak memiliki klausul berisiko."
    
    expected_output = [
        {
            "clause": "N/A",
            "risky_text": "Tidak ditemukan klausul yang dapat dianalisis",
            "reason": "Dokumen aman atau tidak dikenali"
        }
    ]
    
    parsed_data = parse_ai_risk_analysis(ai_response)
    assert parsed_data == expected_output, f"Unexpected output: {parsed_data}"

def test_parse_ai_risk_analysis_invalid_format():
    """❌ Test when the AI response format is incorrect or incomplete."""
    ai_response = "Klausul 3: Tidak lengkap"
    
    expected_output = [
        {
            "clause": "N/A",
            "risky_text": "Tidak ditemukan klausul yang dapat dianalisis",
            "reason": "Dokumen aman atau tidak dikenali"
        }
    ]
    
    parsed_data = parse_ai_risk_analysis(ai_response)
    assert parsed_data == expected_output, f"Unexpected output: {parsed_data}"

# ==========================
# Performance & Scaling Tests
# ==========================

def test_parse_ai_risk_analysis_large_input():
    """✅ Test parsing a large AI response to ensure performance holds up."""
    ai_response = "\n".join([
        f'Klausul {i}: "Klausul contoh {i}". Alasan: "Alasan contoh {i}."' for i in range(1, 51)
    ])
    
    parsed_data = parse_ai_risk_analysis(ai_response)

    assert len(parsed_data) == 50, f"Expected 50 clauses, but got {len(parsed_data)}"
    assert parsed_data[0]["clause"] == "Klausul 1"
    assert parsed_data[-1]["clause"] == "Klausul 50"

