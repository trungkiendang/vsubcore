from flask import Flask, request, jsonify
import os
import sys
import shutil

app = Flask(__name__)

@app.route('/')
def index():
    return app.send_static_file('index.html')

def build_static_site():
    """Build static site for GitHub Pages"""
    # Create _site directory
    site_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '_site')
    if os.path.exists(site_dir):
        shutil.rmtree(site_dir)
    os.makedirs(site_dir, exist_ok=True)
    
    # Copy static files
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
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