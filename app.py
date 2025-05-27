import os
import uuid
import subprocess
from flask import Flask, request, render_template, send_file, url_for, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
STATIC_FOLDER = 'static'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)  # doar dacă nu există deja

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('word_file')
        if not file:
            return "Nu ai încărcat niciun fișier", 400

        unique_id = str(uuid.uuid4())
        filename =  file.filename
        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(upload_path)

        pdf_filename = filename.rsplit('.', 1)[0] + '.pdf'
        pdf_path = os.path.join(CONVERTED_FOLDER, pdf_filename)

        command = [
            'soffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', CONVERTED_FOLDER,
            upload_path
        ]
        subprocess.run(command, check=True)

        download_url = url_for('download_file', filename=pdf_filename)
        return render_template('converted.html', download_url=download_url, original_name=file.filename)

    return render_template('index.html')


@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(CONVERTED_FOLDER, filename), as_attachment=True)


# Ruta custom pentru fisiere statice (CSS, JS, imagini etc)
@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory(STATIC_FOLDER, filename)


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
