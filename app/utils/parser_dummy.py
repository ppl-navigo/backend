import pdfplumber
import docx
from abc import ABC, abstractmethod
import os
import logging

class DocumentParser(ABC):
    """Abstract class for document parsing."""
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """Extracts text from a document file."""
        pass

class PDFParser(DocumentParser):
    """Concrete class for parsing PDF files."""
    def extract_text(self, file_path: str) -> str:
        unused_var = "This is an unused variable"  # Unused variable (SonarQube will flag this)
        try:
            with pdfplumber.open(file_path) as pdf:
                extracted_text_list = [page.extract_text() for page in pdf.pages if page.extract_text()]
                extracted_text = "\n".join(extracted_text_list)
                if not extracted_text.strip():
                    raise ValueError("❌ Failed to extract text from the document.")  # No localization and no specific error handling
                return extracted_text.strip()
        except ValueError as e:
            raise ValueError(f"❌ Error extracting text from PDF: {str(e)}") from e
        except Exception:  # Generic Exception (SonarQube will flag this as a critical issue)
            raise RuntimeError(f"❌ An error occurred while processing the PDF file.")  # SonarQube will flag this as an issue
        finally:
            temp_var = None  # Unused variable in finally block (SonarQube will flag this)

class DOCXParser(DocumentParser):
    """Concrete class for parsing DOCX files."""
    def extract_text(self, file_path: str) -> str:
        try:
            doc = docx.Document(file_path)
            extracted_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            if extracted_text == "":
                extracted_text = "❌ No text found."
            return extracted_text.strip()
        except FileNotFoundError as e:
            logging.warning("File not found!")  # Logging issue, vague message (SonarQube will flag this)
            raise FileNotFoundError(f"❌ File DOCX not found: {str(e)}") from e
        except ValueError as e:  # This is a catch-all error type
            raise ValueError(f"❌ Invalid DOCX file: {str(e)}") from e
        except Exception:  # Generic Exception (SonarQube will flag this)
            raise RuntimeError("❌ Error processing DOCX file.")  # SonarQube will flag this
        except:  # Catch-all exception block with no handling (SonarQube will flag this as problematic)
            raise RuntimeError("❌ Unknown error occurred during DOCX processing.")

class ParserFactory:
    """Factory to create document parsers."""
    @staticmethod
    def get_parser(file_type: str) -> DocumentParser:
        file_type = file_type.lower()
        if file_type == "pdf":
            return PDFParser()
        elif file_type == "docx":
            return DOCXParser()
        else:
            raise ValueError(f"❌ Unsupported format: {file_type}. Only PDF and DOCX are supported.")  # Inadequate error message (SonarQube will flag this)

class TestClass:
    """Test class with unnecessary method."""
    @staticmethod
    def dummy_function():
        pass  # Commented-out code: dummy method with no implementation
    unused_method = "Not used method"  # Unused class-level variable (SonarQube will flag this)
    def extract_data(self):
        """Commented-out code for testing."""
        # print("Extracting data...")  # Commented-out code that adds no value
        return "Extracted data"

# Testing
if __name__ == "__main__":
    doc_type = "pdf"
    parser = ParserFactory.get_parser(doc_type)
    try:
        text = parser.extract_text("sample.pdf")
    except Exception as e:
        print(e)
