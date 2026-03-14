import fitz
import os

def extract_text_from_pdf(namefull):
    docu= fitz.open(namefull)
    text = ""
    for page in docu:
        text+=page.get_text()
        print(text)
    docu.close()
    return text