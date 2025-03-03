import pdfplumber
import docx
from abc import ABC, abstractmethod

class DocumentParser(ABC):
    """Abstract class for document parsing (SOLID - Open/Closed Principle)."""
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """Extracts text from a document file."""
        raise NotImplementedError("Subclasses must implement `extract_text`.")

class PDFParser(DocumentParser):
    """Concrete class for parsing PDF files."""
    def extract_text(self, file_path: str) -> str:
        try:
            with pdfplumber.open(file_path) as pdf:
                extracted_text_list = [page.extract_text() for page in pdf.pages if page.extract_text()]
                extracted_text = "\n".join(extracted_text_list)
                return extracted_text.strip() if extracted_text.strip() else "❌ Gagal mengekstrak teks atau dokumen kosong."
        except pdfplumber.PDFSyntaxError as e:
            raise ValueError(f"❌ PDF rusak atau tidak dapat diproses: {str(e)}") from e
        except FileNotFoundError as e:
            raise FileNotFoundError(f"❌ File PDF tidak ditemukan: {str(e)}") from e
        except IOError as e:
            raise IOError(f"❌ Kesalahan akses file PDF: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"❌ Terjadi kesalahan saat memproses PDF: {str(e)}") from e

class DOCXParser(DocumentParser):
    """Concrete class for parsing DOCX files."""
    def extract_text(self, file_path: str) -> str:
        try:
            doc = docx.Document(file_path)
            extracted_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            return extracted_text.strip() if extracted_text.strip() else "❌ Gagal mengekstrak teks atau dokumen kosong."
        except FileNotFoundError as e:
            raise FileNotFoundError(f"❌ File DOCX tidak ditemukan: {str(e)}") from e
        except IOError as e:
            raise IOError(f"❌ Kesalahan akses file DOCX: {str(e)}") from e
        except ValueError as e:
            raise ValueError(f"❌ File DOCX tidak valid: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"❌ Terjadi kesalahan saat memproses DOCX: {str(e)}") from e

class ParserFactory:
    """Factory Pattern to create document parsers (SOLID - Single Responsibility Principle)."""
    @staticmethod
    def get_parser(file_type: str) -> DocumentParser:
        file_type = file_type.lower()
        if file_type == "pdf":
            return PDFParser()
        elif file_type == "docx":
            return DOCXParser()
        else:
            raise ValueError(f"❌ Format {file_type} tidak didukung! Hanya mendukung PDF dan DOCX.")
