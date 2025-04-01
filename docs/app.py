from flask import Flask, send_from_directory
import os
import sys
import shutil

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/css/<path:filename>')
def css(filename):
    return send_from_directory('css', filename)

def build_static_site():
    """Build static site for GitHub Pages"""
    # Create _site directory
    site_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '_site')
    if os.path.exists(site_dir):
        shutil.rmtree(site_dir)
    os.makedirs(site_dir, exist_ok=True)
    
    # Copy all files from docs directory
    for item in os.listdir('.'):
        if item != '_site' and item != 'app.py':
            if os.path.isfile(item):
                shutil.copy2(item, os.path.join(site_dir, item))
            elif os.path.isdir(item):
                shutil.copytree(item, os.path.join(site_dir, item), dirs_exist_ok=True)
    
    # Create .nojekyll file to prevent GitHub Pages from processing with Jekyll
    with open(os.path.join(site_dir, '.nojekyll'), 'w') as f:
        f.write('')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'build':
        build_static_site()
    else:
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 