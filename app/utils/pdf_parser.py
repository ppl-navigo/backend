import pdfplumber
from abc import ABC, abstractmethod

class DocumentParser(ABC):
    """Abstract class for document parsing (SOLID - Open/Closed Principle)."""
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        pass

class PDFParser(DocumentParser):
    """Concrete class for parsing PDF files."""
    def extract_text(self, file_path: str) -> str:
        try:
            with pdfplumber.open(file_path) as pdf:
                extracted_text_list = [page.extract_text() for page in pdf.pages if page.extract_text()]
                extracted_text = "\n".join(extracted_text_list)
                return extracted_text if extracted_text.strip() else "❌ Gagal mengekstrak teks atau dokumen kosong."
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")

# Factory Pattern to create parsers (SOLID - Single Responsibility Principle)
class ParserFactory:
    @staticmethod
    def get_parser(file_type: str) -> DocumentParser:
        if file_type.lower() == "pdf":
            return PDFParser()
        else:
            raise ValueError(f"❌ Format {file_type} tidak didukung!")

