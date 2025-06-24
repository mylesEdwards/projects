import spacy
import re

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

def extract_info(resume_text):
    # Clean up text
    resume_text = re.sub(r'\s+', ' ', resume_text)

    # Extract with spaCy
    doc = nlp(resume_text)

    name = ""
    organizations = []
    dates = []

    # Regex patterns
    email = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resume_text)
    phone = re.search(r'(\+?\d{1,3}[\s\-]?\d{2,4}[\s\-]?\d{3,5}[\s\-]?\d{3,5})', resume_text)
    linkedin = re.search(r'https?:\/\/(www\.)?linkedin\.com\/[^\s,]+', resume_text)

    # Entity recognition for name, orgs, dates
    for ent in doc.ents:
        if ent.label_ == "PERSON" and name == "":
            name = ent.text.strip()
        elif ent.label_ == "ORG":
            organizations.append(ent.text.strip())
        elif ent.label_ == "DATE":
            dates.append(ent.text.strip())

    return {
        "name": name,
        "email": email.group() if email else "",
        "phone": phone.group() if phone else "",
        "linkedin": linkedin.group() if linkedin else "",
        "organizations": list(set(organizations)),
        "dates": list(set(dates)),
    }

# Run the extractor
if __name__ == "__main__":
    with open("sample_resume.txt", "r", encoding="utf-8") as file:
        resume_text = file.read()
        extracted = extract_info(resume_text)
        for key, value in extracted.items():
            print(f"{key}: {value}")
