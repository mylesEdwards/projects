# resume_data_utils.py

import os
import spacy
import json
import csv
from collections import Counter
import pdfplumber
import docx
import re

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Skills keywords
SKILLS = [
    'python', 'java', 'c++', 'sql', 'javascript', 'html', 'css', 'machine learning',
    'deep learning', 'flask', 'django', 'aws', 'git', 'linux', 'docker', 'excel',
    'communication', 'canva', 'microsoft office', 'jasp'
]

# Helper to extract text from file
def extract_text(file_path):
    if file_path.endswith('.pdf'):
        with pdfplumber.open(file_path) as pdf:
            return ''.join(page.extract_text() or '' for page in pdf.pages)
    elif file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    return None

# Extract email
def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else "Not Found"

# Extract phone
def extract_phone(text):
    match = re.search(r'\+?\d[\d\s\-]{7,}\d', text)
    return match.group(0) if match else "Not Found"

# Parse a single resume
def parse_resume(file_path):
    text = extract_text(file_path)
    if not text:
        return {}

    doc = nlp(text)
    name = next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), "Not Found")
    email = extract_email(text)
    phone = extract_phone(text)
    organizations = list(set(ent.text for ent in doc.ents if ent.label_ == "ORG"))
    dates = list(set(ent.text for ent in doc.ents if ent.label_ == "DATE"))
    locations = list(set(ent.text for ent in doc.ents if ent.label_ == "GPE"))
    skills_found = [skill for skill in SKILLS if skill.lower() in text.lower()]
    education = [org for org in organizations if any(word in org for word in ["University", "College", "School", "Institute"])]

    work_experience = []
    for line in text.split('\n'):
        if any(keyword in line.lower() for keyword in ["experience", "worked at", "responsible for", "employment", "internship"]):
            work_experience.append(line.strip())

    return {
        'Name': name.title(),
        'Email': email,
        'Phone': phone,
        'Organizations': organizations,
        'Dates': dates,
        'Locations': locations,
        'Skills': skills_found,
        'Education': education,
        'Work Experience': work_experience
    }

# Clean a single parsed resume
def clean_data(data):
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = value.strip()
        elif isinstance(value, list):
            data[key] = list(set([v.strip() for v in value if v.strip()]))
    return data

# Tag resume based on skills
def tag_resume(data):
    if len(data.get('Skills', [])) > 8:
        data['Skill_Level'] = 'Advanced'
    elif len(data.get('Skills', [])) > 3:
        data['Skill_Level'] = 'Intermediate'
    else:
        data['Skill_Level'] = 'Beginner'

    edu = ' '.join(data.get('Education', [])).lower()
    if 'master' in edu or 'msc' in edu:
        data['Education_Level'] = 'Master'
    elif 'bachelor' in edu or 'bsc' in edu:
        data['Education_Level'] = 'Bachelor'
    else:
        data['Education_Level'] = 'Unknown'
    return data

# Parse and clean all resumes in folder
def process_folder(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    all_data = []

    for filename in os.listdir(input_folder):
        if filename.endswith('.pdf') or filename.endswith('.docx'):
            file_path = os.path.join(input_folder, filename)
            parsed = parse_resume(file_path)
            parsed = clean_data(parsed)
            parsed = tag_resume(parsed)
            parsed['Filename'] = filename
            all_data.append(parsed)

    # Save compiled dataset
    output_csv = os.path.join(output_folder, 'compiled_resumes.csv')
    output_json = os.path.join(output_folder, 'compiled_resumes.json')

    if all_data:
        with open(output_json, 'w') as jf:
            json.dump(all_data, jf, indent=4)

        with open(output_csv, 'w', newline='') as cf:
            writer = csv.DictWriter(cf, fieldnames=all_data[0].keys())
            writer.writeheader()
            for row in all_data:
                writer.writerow(row)

    return all_data

# Analyze parsed data

def generate_analysis_report(all_data, output_folder):
    skills_counter = Counter()
    education_levels = Counter()

    for entry in all_data:
        skills_counter.update(entry.get('Skills', []))
        education_levels.update([entry.get('Education_Level', 'Unknown')])

    report = {
        'Total_Resumes': len(all_data),
        'Top_Skills': skills_counter.most_common(10),
        'Education_Levels': dict(education_levels)
    }

    report_path = os.path.join(output_folder, 'analysis_report.json')
    with open(report_path, 'w') as rf:
        json.dump(report, rf, indent=4)

    return report