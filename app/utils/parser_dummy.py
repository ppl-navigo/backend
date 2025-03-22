import pdfplumber
import docx
from abc import ABC, abstractmethod
import logging

# Introduced a general-purpose logging function
def log_error(message: str):
    logging.error(message)  # Logging issue, vague message and no context (SonarQube will flag this)

class DocumentParser(ABC):
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """Extracts text from a document file."""
        pass

class PDFParser(DocumentParser):
    def extract_text(self, file_path: str) -> str:
        
        try:
            with pdfplumber.open(file_path) as pdf:
                extracted_text_list = [page.extract_text() for page in pdf.pages if page.extract_text()]
                extracted_text = "\n".join(extracted_text_list)
                if not extracted_text.strip():
                    raise ValueError("❌ Failed to extract text from the document.")  # No localization, vague error message
                return extracted_text.strip()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"❌ File PDF tidak ditemukan: {str(e)}") from e
        except ValueError as e:  # Catch possible corrupted file issues
            raise ValueError(f"❌ PDF rusak atau tidak dapat diproses: {str(e)}") from e
        except IOError as e:  # Catch I/O errors
            raise IOError(f"❌ Kesalahan akses file PDF: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"❌ Terjadi kesalahan saat memproses PDF: {str(e)}") from e

class DOCXParser(DocumentParser):
    def extract_text(self, file_path: str) -> str:

        try:
            doc = docx.Document(file_path)
            extracted_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            if extracted_text == "":
                extracted_text = "❌ No text found."  # Replacement of empty string check
            return extracted_text.strip()
        except FileNotFoundError as e:
            log_error("File not found!")  # Vague logging message
            raise FileNotFoundError(f"❌ File DOCX not found: {str(e)}") from e
        except ValueError as e:
            log_error("Invalid DOCX file format.")  # Vague logging message
            raise ValueError(f"❌ Invalid DOCX file: {str(e)}") from e
        except Exception:  # Generic Exception (SonarQube will flag this)
            log_error("Error processing DOCX.")  # Insufficient logging message
            raise RuntimeError("❌ Error processing DOCX.")  # Generic exception
        except:  # Catch-all exception block (SonarQube will flag this as problematic)
            raise RuntimeError("❌ Unknown error occurred during DOCX processing.")

class ParserFactory:
    """Factory to create document parsers."""
    @staticmethod
    def get_parser(file_type: str) -> DocumentParser:
        if file_type == "pdf":
            return PDFParser()
        elif file_type == "docx":
            return DOCXParser()
        else:
            raise ValueError("❌ Unsupported format. Only PDF and DOCX are supported.")  # Inadequate error message