import pandas as pd
from pypdf import PdfReader
from docx import Document

MAX_CHARACTERS = 4000


def extract_from_spreadsheet(uploaded_file):
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        text = df.head(50).to_string(index=False)
        return truncate_text(text)
    except Exception as e:
        return f"[Could not read spreadsheet: {e}]"


def extract_from_pdf(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return truncate_text(text)
    except Exception as e:
        return f"[Could not read PDF: {e}]"


def extract_from_docx(uploaded_file):
    try:
        doc = Document(uploaded_file)
        text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
        return truncate_text(text)
    except Exception as e:
        return f"[Could not read Word document: {e}]"


def truncate_text(text):
    if len(text) > MAX_CHARACTERS:
        return text[:MAX_CHARACTERS] + "\n[...truncated for length...]"
    return text


def extract_document_text(uploaded_file):
    filename = uploaded_file.name.lower()

    if filename.endswith((".xlsx", ".xls", ".csv")):
        return extract_from_spreadsheet(uploaded_file)
    elif filename.endswith(".pdf"):
        return extract_from_pdf(uploaded_file)
    elif filename.endswith(".docx"):
        return extract_from_docx(uploaded_file)
    else:
        return "[Unsupported file type]"
    