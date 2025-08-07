import os
import io
import requests
import mimetypes
import fitz  # PyMuPDF
from docx import Document
import extract_msg
from email import policy
from email.parser import BytesParser

# Testing
import easyocr
import requests
from tempfile import NamedTemporaryFile

reader = easyocr.Reader(['en'])  # only downloads a small model

def extract_text_easyocr(url):
    response = requests.get(url)
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(response.content)
        pdf_path = tmp_file.name

    result = reader.readtext(pdf_path, detail=0, paragraph=True)
    return "\n".join(result)


import subprocess
import requests
from tempfile import NamedTemporaryFile
from bs4 import BeautifulSoup
import os

def extract_text_pdf2html(url):
    response = requests.get(url)
    with NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
        pdf_file.write(response.content)
        pdf_path = pdf_file.name

    html_path = pdf_path.replace(".pdf", ".html")

    subprocess.run(["pdf2htmlEX", "--quiet", pdf_path, html_path])

    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Collect visible text from divs
    divs = soup.find_all("div")
    texts = [div.get_text(separator=" ", strip=True) for div in divs]
    texts = [text for text in texts if text]

    return "\n\n".join(texts)


# from paddleocr import PaddleOCR
# import requests
# from tempfile import NamedTemporaryFile

# ocr = PaddleOCR(use_angle_cls=True, lang='en')

# def extract_text_paddleocr(url):
#     response = requests.get(url)
#     with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
#         tmp_file.write(response.content)
#         pdf_path = tmp_file.name

#     result = ocr.ocr(pdf_path)
#     texts = []

#     for page in result:
#         for line in page:
#             _, (text, _) = line
#             texts.append(text)

#     return "\n".join(texts)


# Production

def extract_text(url: str) -> str:
    # Step 1: Download the file
    response = requests.get(url)
    response.raise_for_status()
    content = response.content

    # Step 2: Detect file type
    content_type = response.headers.get("Content-Type") or mimetypes.guess_type(url)[0] or ""

    if "pdf" in content_type or url.lower().endswith(".pdf"):
        return extract_pdf_text(content)
    elif "word" in content_type or url.lower().endswith(".docx"):
        return extract_docx_text(content)
    elif url.lower().endswith(".eml"):
        return extract_eml_text(content)
    elif url.lower().endswith(".msg"):
        return extract_msg_text(content)
    else:
        raise ValueError(f"Unsupported file type or extension: {content_type}")

def extract_pdf_text(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")
    text = "\n".join([page.get_text() for page in doc])
    doc.close()
    return text

def extract_docx_text(docx_bytes: bytes) -> str:
    with io.BytesIO(docx_bytes) as f:
        doc = Document(f)
        return "\n".join([p.text for p in doc.paragraphs])

def extract_eml_text(eml_bytes: bytes) -> str:
    msg = BytesParser(policy=policy.default).parsebytes(eml_bytes)
    parts = []
    if msg['subject']:
        parts.append(f"Subject: {msg['subject']}")
    if msg['from']:
        parts.append(f"From: {msg['from']}")
    if msg['to']:
        parts.append(f"To: {msg['to']}")
    if msg.get_body(preferencelist=('plain')):
        parts.append(msg.get_body(preferencelist=('plain')).get_content())
    return "\n".join(parts)

def extract_msg_text(msg_bytes: bytes) -> str:
    with open("temp.msg", "wb") as f:
        f.write(msg_bytes)
    msg = extract_msg.Message("temp.msg")
    text = f"Subject: {msg.subject}\nFrom: {msg.sender}\nTo: {msg.to}\n\n{msg.body}"
    os.remove("temp.msg")
    return text



# TEMPORARY
from difflib import SequenceMatcher

def similarity_score(str1: str, str2: str) -> float:
    """
    Returns a similarity score between 0 and 1, where 1 means identical strings.
    """
    return SequenceMatcher(None, str1, str2).ratio()

# Example usage:
def score_checker(answers):
    expected = [
        "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
        "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
        "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period.",
        "The policy has a specific waiting period of two (2) years for cataract surgery.",
        "Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person and the donation complies with the Transplantation of Human Organs Act, 1994.",
        "A No Claim Discount of 5% on the base premium is offered on renewal for a one-year policy term if no claims were made in the preceding year. The maximum aggregate NCD is capped at 5% of the total base premium.",
        "Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, provided the policy has been renewed without a break. The amount is subject to the limits specified in the Table of Benefits.",
        "A hospital is defined as an institution with at least 10 inpatient beds (in towns with a population below ten lakhs) or 15 beds (in all other places), with qualified nursing staff and medical practitioners available 24/7, a fully equipped operation theatre, and which maintains daily records of patients.",
        "The policy covers medical expenses for inpatient treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy systems up to the Sum Insured limit, provided the treatment is taken in an AYUSH Hospital.",
        "Yes, for Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN)."
    ]
    score = 0
    for ans, expt in zip(answers, expected):
        sim = similarity_score(ans, expt)
        score += sim
        print(sim)
    return score/len(expected)
