from pypdf import PdfReader

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

pdf_file_path = 'japanese_text/heike_pdf_eng.pdf'
raw_text = extract_text_from_pdf(pdf_file_path)
print(raw_text)

with open('heike_pdf.txt', 'w', encoding='utf-8') as f:
    f.write(raw_text)   