

import spacy
import re
import pdfplumber
import docx
import os
import json
import csv

# Load spaCy model once
nlp = spacy.load("en_core_web_sm")

# Define skills keywords
SKILLS = [
    'python', 'java', 'c++', 'sql', 'javascript', 'html', 'css', 'machine learning',
    'deep learning', 'flask', 'django', 'aws', 'git', 'linux', 'docker', 'excel',
    'communication', 'canva', 'microsoft office', 'jasp'
]

# Helper: Extract text from file
def extract_text(file_path):
    if file_path.endswith('.pdf'):
        with pdfplumber.open(file_path) as pdf:
            return ''.join(page.extract_text() or '' for page in pdf.pages)
    elif file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    else:
        return None

# Helper: Extract email
def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else "Not Found"

# Helper: Extract phone number
def extract_phone(text):
    match = re.search(r'\+?\d[\d\s\-]{7,}\d', text)
    return match.group(0) if match else "Not Found"

# Main: Parse resume fields
def parse_resume(file_path):
    text = extract_text(file_path)
    if not text:
        return {}

    doc = nlp(text)

    # Entity Extraction
    name = next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), "Not Found")
    email = extract_email(text)
    phone = extract_phone(text)
    organizations = list(set(ent.text for ent in doc.ents if ent.label_ == "ORG"))
    dates = list(set(ent.text for ent in doc.ents if ent.label_ == "DATE"))
    locations = list(set(ent.text for ent in doc.ents if ent.label_ == "GPE"))

    # Skills detection
    found_skills = [skill for skill in SKILLS if skill.lower() in text.lower()]

    # Education detection
    education = [org for org in organizations if any(word in org for word in ["University", "College", "School", "Institute"])]

    # Work experience detection
    work_experience = []
    lines = text.split('\n')
    for line in lines:
        if any(keyword in line.lower() for keyword in ["experience", "worked at", "responsible for", "employment", "internship"]):
            work_experience.append(line.strip())

    return {
        'Name': name,
        'Email': email,
        'Phone': phone,
        'Organizations': organizations,
        'Dates': dates,
        'Locations': locations,
        'Skills': found_skills,
        'Education': education,
        'Work Experience': work_experience
    }

# Save parsed data to JSON and CSV
def save_parsed_data(data, output_folder, filename_prefix):
    os.makedirs(output_folder, exist_ok=True)

    # Save as JSON
    with open(os.path.join(output_folder, f"{filename_prefix}.json"), 'w') as jf:
        json.dump(data, jf, indent=4)

    # Save as CSV
    with open(os.path.join(output_folder, f"{filename_prefix}.csv"), 'w', newline='') as cf:
        writer = csv.DictWriter(cf, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)
