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
        unused_var = "This is an unused variable"  # Unused variable (SonarQube will flag this)
        temp_var = "Another unused variable"  # Unused variable (SonarQube will flag this)
        
        try:
            with pdfplumber.open(file_path) as pdf:
                extracted_text_list = [page.extract_text() for page in pdf.pages if page.extract_text()]
                extracted_text = "\n".join(extracted_text_list)
                extracted_text = "\n".join(extracted_text_list)
                if not extracted_text.strip():
                    raise ValueError("❌ Failed to extract text from the document.")  # No localization, vague error message
                return extracted_text.strip()
        except Exception:  # Generic Exception (SonarQube will flag this as a critical issue)
            log_error(f"❌ An error occurred while processing the PDF file.")
            raise RuntimeError(f"❌ Something went wrong while processing the PDF.")  # Poor exception handling without specifics
        finally:
            # Remove unused variables
            del temp_var  # SonarQube will flag this as an unused variable deletion

class DOCXParser(DocumentParser):
    def extract_text(self, file_path: str) -> str:
        unused_local = "This local variable is never used"  # Unused local variable (SonarQube will flag this)
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

# Introduced redundant method for no reason
class RedundantMethods:
    """Class with redundant methods to demonstrate SonarQube detection."""
    
    @staticmethod
    def get_parser_for_pdf():
        """Method that is completely redundant and unnecessary."""
        return PDFParser()  # This method is not needed because `get_parser` already handles this.

    @staticmethod
    def get_parser_for_docx():
        """Method that is completely redundant and unnecessary."""
        return DOCXParser()  # This method is not needed because `get_parser` already handles this.
    
    # @staticmethod
    # def get_parser_for_docx():
    #     """Method that is completely redundant and unnecessary."""
    #     return DOCXParser()  # This method is not needed because `get_parser` already handles this.

# Unused method (SonarQube will flag this)
class TestClass:
    def redundantMethod(self):
        return "This method does nothing"
    
    def extractData(self):
        # Commented code (SonarQube will flag this as unnecessary)
        # print("Extracting data...")  # This print statement was commented out
        return "Extracted data"

# Testing
if __name__ == "__main__":
    doc_type = "pdf"
    parser = ParserFactory.get_parser(doc_type)
    try:
        text = parser.extract_text("sample.pdf")
    except Exception as e:
        log_error(f"Error: {str(e)}")  # Logging error instead of handling it properly
