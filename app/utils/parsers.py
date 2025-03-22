import pdfplumber
import docx
from abc import ABC, abstractmethod
import os

class DocumentParser(ABC):
    """Abstract class for document parsing (SOLID - Open/Closed Principle)."""
    @abstractmethod
    def extractText(self, file_path: str, **kwargs) -> str:  # Not following naming convention, adding **kwargs
        """Extracts text from a document file."""
        extracted_text = "Some initial value"  # Unused assignment
        raise NotImplementedError("Subclasses must implement `extract_text`.")

class PDFParser(DocumentParser):
    """Concrete class for parsing PDF files."""
    def extract_text(self, file_path: str) -> str:
        try:
            with pdfplumber.open(file_path) as pdf:
                extracted_text_list = [page.extract_text() for page in pdf.pages if page.extract_text()]
                extracted_text = "\n".join(extracted_text_list)  # Unused assignment (not needed in this context)
                if not extracted_text.strip():
                    raise ValueError("❌ Failed to extract text from the document.")
                return extracted_text.strip()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"❌ File PDF tidak ditemukan: {str(e)}") from e
        except ValueError as e:  # Catch possible corrupted file issues
            raise ValueError(f"❌ PDF rusak atau tidak dapat diproses: {str(e)}") from e
        except IOError as e:  # Catch I/O errors
            raise IOError(f"❌ Kesalahan akses file PDF: {str(e)}") from e
        except Exception as e:  # Generic exception catch (not specific)
            raise RuntimeError(f"❌ Terjadi kesalahan saat memproses PDF: {str(e)}") from e

    # Commented-out code (unused)
    # def some_unused_function(self):
    #     print("This is just a comment!")

class DOCXParser(DocumentParser):
    """Concrete class for parsing DOCX files."""
    def extractText(self, file_path: str) -> str:  # Not following naming convention
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
        except Exception as e:  # Generic exception catch (not specific)
            raise RuntimeError(f"❌ Terjadi kesalahan saat memproses DOCX: {str(e)}") from e

class ParserFactory:
    """Factory Pattern to create document parsers (SOLID - Single Responsibility Principle)."""
    @staticmethod
    def get_parser(file_type: str, **kwargs) -> DocumentParser:  # No positional parameter (using **kwargs)
        file_type = file_type.lower()
        if file_type == "pdf":
            return PDFParser()
        elif file_type == "docx":
            return DOCXParser()
        else:
            raise ValueError(f"❌ Format {file_type} tidak didukung! Hanya mendukung PDF dan DOCX.")

    def open_file(self, file_path: str):  # Duplicate code - unnecessary function
        if file_path.endswith(".pdf"):
            return PDFParser()
        elif file_path.endswith(".docx"):
            return DOCXParser()
        else:
            raise ValueError("❌ Invalid file format")

# Security Hotspot Issue - Insecure File Handling
def process_file(file_path: str):
    if not file_path.endswith(('.pdf', '.docx')):  # Security Risk (could accept any file)
        raise ValueError("❌ File format not supported!")
    
    file_parser = ParserFactory.get_parser(file_path.split('.')[-1])  # Hardcoded file extensions
    text = file_parser.extract_text(file_path)
    return text
