import fitz  # PyMuPDF

def extract_text_from_pdf(file_path):
    """Extract text from a PDF."""
    with fitz.open(file_path) as pdf:
        text = ""
        for page in pdf:
            text += page.get_text()
    return text
