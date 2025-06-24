from flask import Flask, render_template, request, redirect, session, url_for
import os
import json
from resume_data_utils import parse_resume, clean_data, tag_resume, process_folder
#generate_analysis_report
#from openai_feedback import generate_resume_feedback_ai


# Flask App Setup
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload/output folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Routes

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'pass':
            session['user'] = username
            return redirect(url_for('upload_form'))
        else:
            error = '❌ Invalid username or password.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/upload-form')
def upload_form():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files:
        return 'No file part'
    file = request.files['resume']
    if file.filename == '':
        return 'No selected file'

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    data = parse_resume(file_path)
    if not data:
        return 'Unsupported file format or no data extracted'

    data = clean_data(data)
    data = tag_resume(data)

    # Save parsed resume individually
    output_folder = 'output'
    filename_prefix = os.path.splitext(file.filename)[0]

    # Save as JSON
    with open(os.path.join(output_folder, f'{filename_prefix}.json'), 'w') as jf:
        json.dump(data, jf, indent=4)

    # Save as CSV
    with open(os.path.join(output_folder, f'{filename_prefix}.csv'), 'w', newline='') as cf:
        import csv
        writer = csv.DictWriter(cf, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)

    # ✨ NEW: Generate AI feedback
    resume_text = data.get("FullText", "") or "\n".join(data.get("Work Experience", []))
    #feedback = generate_resume_feedback_ai(resume_text)

    # ⬇️ Pass feedback to template
    return render_template('result.html', data=data, )#feedback=feedback


@app.route('/analyze')
def analyze_data():
    all_data = process_folder('uploads', 'output')
    report = generate_analysis_report(all_data, 'output')
    return render_template('analysis.html', report=report)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5051)
