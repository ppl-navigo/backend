import pdfplumber

def extract_text_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            extracted_text_list = [page.extract_text() for page in pdf.pages if page.extract_text()]
            extracted_text = "\n".join(extracted_text_list)
            return extracted_text if extracted_text.strip() else "❌ Gagal mengekstrak teks atau dokumen kosong."
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")
