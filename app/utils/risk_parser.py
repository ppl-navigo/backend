import re
from typing import List, Dict

def parse_ai_risk_analysis(ai_response: str) -> List[Dict[str, str]]:
    """
    Parses AI-generated risk analysis response into structured format.
    Expected format:
    - Klausul {nomor}: "{kalimat berisiko}" Alasan: "{penjelasan}".
    """
    # Updated pattern to allow newlines or spaces plus optional period
    pattern = r'Klausul\s+(\d+):\s*"(.*?)"\s*\.?\s*Alasan:\s*"(.*?)"'
    matches = re.findall(pattern, ai_response, re.DOTALL | re.MULTILINE)

    if not matches:
        return [{
            "clause": "N/A",
            "risky_text": "Tidak ditemukan klausul yang dapat dianalisis",
            "reason": "Dokumen aman atau tidak dikenali"
        }]

    structured_results = [
        {
            "clause": f"Klausul {match[0]}",
            "risky_text": match[1].strip(),
            "reason": match[2].strip()
        }
        for match in matches
    ]

    return structured_results