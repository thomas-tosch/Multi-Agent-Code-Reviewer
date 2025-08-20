from flask import Flask, request, render_template, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import logging
import zipfile
import tempfile
from typing import Dict, Any

from package.agents.orchestrator import ReviewOrchestrator
from package.utils.file_processor import FileProcessor
from package.config import DEBUG, ALLOWED_EXTENSIONS, MAX_FILE_SIZE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

orchestrator = ReviewOrchestrator()
file_processor = FileProcessor()

@app.route('/')
def index():
    return render_template('index.html', 
                         allowed_extensions=list(ALLOWED_EXTENSIONS),
                         max_size_mb=MAX_FILE_SIZE // (1024 * 1024))

@app.route('/review', methods=['POST'])
def review():
    try:
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                return handle_file_upload(file)
        
        if 'code' in request.form:
            code = request.form['code']
            if code.strip():
                results = orchestrator.review_code(code)
                return render_template('results.html', 
                                     results=results,
                                     code=code,
                                     mode='single')
        
        flash('Please provide code to review', 'error')
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Error during review: {str(e)}")
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/review-repository', methods=['POST'])
def review_repository():
    try:
        if 'repository' not in request.files:
            flash('No repository file uploaded', 'error')
            return redirect(url_for('index'))
        
        file = request.files['repository']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        if file and file.filename.endswith('.zip'):
            return handle_repository_upload(file)
        else:
            flash('Please upload a ZIP file', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Error during repository review: {str(e)}")
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/review', methods=['POST'])
def api_review():
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({'error': 'No code provided'}), 400
        
        code = data['code']
        context = data.get('context', None)
        
        results = orchestrator.review_code(code, context)
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def handle_file_upload(file):
    filename = secure_filename(file.filename)
    
    ext = os.path.splitext(filename)[1]
    if ext not in ALLOWED_EXTENSIONS:
        flash(f'File type {ext} not supported', 'error')
        return redirect(url_for('index'))
    
    code = file.read().decode('utf-8', errors='ignore')
    
    context = {
        "filename": filename,
        "extension": ext,
        "file_size": len(code)
    }
    
    results = orchestrator.review_code(code, context)
    
    return render_template('results.html',
                         results=results,
                         code=code,
                         filename=filename,
                         mode='file')

def handle_repository_upload(file):
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
        file.save(tmp_file.name)
        tmp_path = tmp_file.name
    
    try:
        files = file_processor.extract_zip(tmp_path)
        
        if not files:
            flash('No valid code files found in ZIP', 'error')
            return redirect(url_for('index'))
        
        results = orchestrator.review_repository(files)
        
        return render_template('results.html',
                             results=results,
                             files=files,
                             mode='repository')
    finally:
        os.unlink(tmp_path)

@app.errorhandler(413)
def file_too_large(e):
    flash('File too large. Maximum size is {} MB'.format(MAX_FILE_SIZE // (1024 * 1024)), 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=DEBUG, port=5000)
