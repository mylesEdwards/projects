from pyresparser import ResumeParser

data = ResumeParser('Vardha_Anand_CV.docx', model=None).get_extracted_data()

for key, value in data.items():
    print(f"{key}: {value}")
