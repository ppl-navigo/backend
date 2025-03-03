import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class RiskParser:
    """Handles AI-generated risk analysis parsing with robust error handling and logging."""

    RISK_PATTERN = r'Klausul\s+(\d+):\s*"(.*?)"\s*\.?\s*Alasan:\s*"(.*?)"'

    @staticmethod
    def parse_ai_risk_analysis(ai_response: str) -> List[Dict[str, str]]:
        """
        Parses AI-generated risk analysis response into a structured format.
        Expected format:
         - Klausul {nomor}: "{kalimat berisiko}" Alasan: "{penjelasan}".
        """
        logger.info(
            "Parsing AI risk analysis response, length=%d",
            len(ai_response)
        )

        try:
            matches = re.findall(
                RiskParser.RISK_PATTERN,
                ai_response,
                re.DOTALL | re.MULTILINE
            )

            if not matches:
                logger.warning("No valid risk clauses found in the AI response")
                return [{
                    "clause": "N/A",
                    "risky_text": "Tidak ditemukan klausul yang dapat dianalisis",
                    "reason": "Dokumen aman atau tidak dikenali"
                }]

            structured_results = [
                {
                    "clause": f"Klausul {m[0]}",
                    "risky_text": m[1].strip(),
                    "reason": m[2].strip()
                }
                for m in matches
            ]

            logger.info(
                "Successfully parsed AI risk analysis, clause_count=%d",
                len(structured_results)
            )
            return structured_results

        except Exception as exc:
            logger.error("Error while parsing AI risk analysis: %s", exc)
            return [{
                "clause": "N/A",
                "risky_text": "Parsing gagal",
                "reason": "Kesalahan sistem saat mengolah dokumen"
            }]
