import pytest
from unittest.mock import patch, MagicMock
from app.utils.parsers import PDFParser, DOCXParser, ParserFactory, DocumentParser  # Adjust import paths accordingly

# ==========================
# Mock Objects
# ==========================

@pytest.fixture
def mock_pdf_with_text():
    """Mock PDF file with extractable text."""
    mock_pdf = MagicMock()
    mock_pdf.__enter__.return_value = mock_pdf  
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Sample extracted text from PDF"
    mock_pdf.pages = [mock_page]
    return mock_pdf

@pytest.fixture
def mock_pdf_no_text():
    """Mock PDF file with no extractable text."""
    mock_pdf = MagicMock()
    mock_pdf.__enter__.return_value = mock_pdf
    mock_page = MagicMock()
    mock_page.extract_text.return_value = None
    mock_pdf.pages = [mock_page]
    return mock_pdf

@pytest.fixture
def mock_pdf_multi_page():
    """Mock multi-page PDF with different page texts."""
    mock_pdf = MagicMock()
    mock_pdf.__enter__.return_value = mock_pdf
    mock_page_1 = MagicMock()
    mock_page_1.extract_text.return_value = "Page 1 content"
    mock_page_2 = MagicMock()
    mock_page_2.extract_text.return_value = "Page 2 content"
    mock_pdf.pages = [mock_page_1, mock_page_2]
    return mock_pdf

@pytest.fixture
def mock_docx_with_text():
    """Mock DOCX file with extractable text."""
    mock_doc = MagicMock()
    mock_doc.paragraphs = [MagicMock(text="Sample extracted text from DOCX")]
    return mock_doc

@pytest.fixture
def mock_docx_no_text():
    """Mock DOCX file with no extractable text."""
    mock_doc = MagicMock()
    mock_doc.paragraphs = [MagicMock(text="")]  # No text available
    return mock_doc

# ==========================
# Tests for PDF Parsing
# ==========================

def test_extract_text_pdf_with_text(mock_pdf_with_text):
    """✅ Test PDF with extractable text."""
    with patch("pdfplumber.open", return_value=mock_pdf_with_text):
        parser = PDFParser()
        extracted_text = parser.extract_text("dummy.pdf")
        assert extracted_text == "Sample extracted text from PDF", f"Unexpected output: {extracted_text}"

def test_extract_text_pdf_no_text(mock_pdf_no_text):
    """✅ Test PDF with no extractable text."""
    with patch("pdfplumber.open", return_value=mock_pdf_no_text):
        parser = PDFParser()
        extracted_text = parser.extract_text("dummy.pdf")
        assert extracted_text == "❌ Gagal mengekstrak teks atau dokumen kosong."

def test_extract_text_pdf_multi_page(mock_pdf_multi_page):
    """✅ Test PDF with multiple pages."""
    with patch("pdfplumber.open", return_value=mock_pdf_multi_page):
        parser = PDFParser()
        extracted_text = parser.extract_text("dummy.pdf")
        expected_text = "Page 1 content\nPage 2 content"
        assert extracted_text == expected_text, f"Unexpected output: {extracted_text}"

# ==========================
# Tests for DOCX Parsing
# ==========================

def test_extract_text_docx_with_text(mock_docx_with_text):
    """✅ Test DOCX with extractable text."""
    with patch("docx.Document", return_value=mock_docx_with_text):
        parser = DOCXParser()
        extracted_text = parser.extract_text("dummy.docx")
        assert extracted_text == "Sample extracted text from DOCX", f"Unexpected output: {extracted_text}"

def test_extract_text_docx_no_text(mock_docx_no_text):
    """✅ Test DOCX with no extractable text."""
    with patch("docx.Document", return_value=mock_docx_no_text):
        parser = DOCXParser()
        extracted_text = parser.extract_text("dummy.docx")
        assert extracted_text == "❌ Gagal mengekstrak teks atau dokumen kosong."

# ==========================
# Tests for ParserFactory
# ==========================

def test_parser_factory_pdf():
    """✅ Ensure ParserFactory returns PDFParser when given 'pdf'."""
    parser = ParserFactory.get_parser("pdf")
    assert isinstance(parser, PDFParser), "Expected instance of PDFParser."

def test_parser_factory_docx():
    """✅ Ensure ParserFactory returns DOCXParser when given 'docx'."""
    parser = ParserFactory.get_parser("docx")
    assert isinstance(parser, DOCXParser), "Expected instance of DOCXParser."

def test_parser_factory_invalid_format():
    """✅ Ensure ParserFactory raises an error for unsupported formats."""
    with pytest.raises(ValueError, match="❌ Format txt tidak didukung! Hanya mendukung PDF dan DOCX."):
        ParserFactory.get_parser("txt")

def test_document_parser_abstract_method():
    """Ensure that calling abstract method raises an error."""
    
    class TestParser(DocumentParser):
        def extract_text(self, file_path: str) -> str:
            return super().extract_text(file_path)  # This should trigger NotImplementedError
    
    parser = TestParser()
    
    with pytest.raises(NotImplementedError, match="must implement `extract_text`"):
        parser.extract_text("dummy.pdf")

# ==========================
# Tests for Error Handling
# ==========================

def test_extract_text_pdf_corrupted_file():
    """✅ Test corrupted PDF file handling."""
    with patch("pdfplumber.open", side_effect=Exception("Corrupted file")):
        parser = PDFParser()
        with pytest.raises(Exception, match="Corrupted file"):
            parser.extract_text("corrupted.pdf")

def test_extract_text_docx_corrupted_file():
    """✅ Test corrupted DOCX file handling."""
    with patch("docx.Document", side_effect=Exception("Corrupted DOCX file")):
        parser = DOCXParser()
        with pytest.raises(Exception, match="Corrupted DOCX file"):
            parser.extract_text("corrupted.docx")

