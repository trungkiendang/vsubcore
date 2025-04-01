from flask import Flask, request, jsonify
import os
import sys
import tempfile
import shutil
from werkzeug.utils import secure_filename

# Import vsub-nolog functions directly from the same directory
from vsub_nolog import find_speech_regions, download_audio, transcribe_audio

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'mp3', 'wav', 'flac'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    language = request.form.get('language', 'en')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the file
        audio_path = download_audio(filepath)
        regions = find_speech_regions(audio_path)
        text = transcribe_audio(audio_path, regions, language)
        
        # Clean up temporary files
        os.remove(filepath)
        os.remove(audio_path)
        
        return jsonify({
            'success': True,
            'text': text,
            'regions': regions
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def build_static_site():
    """Build static site for GitHub Pages"""
    # Create _site directory
    site_dir = os.path.join(os.path.dirname(__file__), '_site')
    if os.path.exists(site_dir):
        shutil.rmtree(site_dir)
    os.makedirs(site_dir, exist_ok=True)
    
    # Copy static files
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    shutil.copytree(static_dir, os.path.join(site_dir, 'static'), dirs_exist_ok=True)
    
    # Copy index.html to root
    shutil.copy2(os.path.join(static_dir, 'index.html'), os.path.join(site_dir, 'index.html'))
    
    # Create .nojekyll file to prevent GitHub Pages from processing with Jekyll
    with open(os.path.join(site_dir, '.nojekyll'), 'w') as f:
        f.write('')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'build':
        build_static_site()
    else:
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 