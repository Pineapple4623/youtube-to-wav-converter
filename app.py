from flask import Flask, request, send_file, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import os
import time
import logging
from datetime import datetime, timedelta
import re
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///downloads.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')
CLEANUP_INTERVAL = 30  # minutes
API_BASE_URL = "https://loader.to/api"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

class Download(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    format = db.Column(db.String(50), nullable=False)
    quality = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()

def is_valid_youtube_url(url):
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^"&?/s]{11})'
    return bool(re.match(youtube_regex, url))

def get_available_formats(url):
    try:
        # Define available formats based on the API documentation
        formats = []
        
        # Add audio formats
        formats.append({
            'type': 'audio',
            'formats': [
                {'id': 'mp3', 'name': 'MP3'},
                {'id': 'm4a', 'name': 'M4A'},
                {'id': 'webm_audio', 'name': 'WEBM Audio'},
                {'id': 'aac', 'name': 'AAC'},
                {'id': 'flac', 'name': 'FLAC'},
                {'id': 'opus', 'name': 'OPUS'},
                {'id': 'ogg', 'name': 'OGG'},
                {'id': 'wav', 'name': 'WAV'}
            ]
        })
        
        # Add video formats
        formats.append({
            'type': 'video',
            'formats': [
                {'id': '360', 'name': 'MP4 360p'},
                {'id': '480', 'name': 'MP4 480p'},
                {'id': '720', 'name': 'MP4 720p'},
                {'id': '1080', 'name': 'MP4 1080p'},
                {'id': '4k', 'name': 'MP4 4K'},
                {'id': '8k', 'name': 'MP4 8K'}
            ]
        })
        
        return formats
    except Exception as e:
        logger.error(f"Error getting formats: {str(e)}")
        return []

def download_media(youtube_url, media_type, quality):
    timestamp = int(time.time())
    
    try:
        # Using the button API for direct download
        api_url = f"{API_BASE_URL}/button/?url={youtube_url}&f={quality}"
        response = requests.get(api_url)
        
        if response.status_code != 200:
            raise Exception("Failed to initiate download")
            
        # The API will handle the download process
        # We'll just record the download in our database
        download = Download(
            filename=f"{media_type}_{timestamp}.{quality}",
            format=media_type,
            quality=quality
        )
        db.session.add(download)
        db.session.commit()
        
        return f"Download initiated for {youtube_url}"
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        raise

def cleanup_old_files():
    with app.app_context():
        cutoff_time = datetime.utcnow() - timedelta(minutes=CLEANUP_INTERVAL)
        old_downloads = Download.query.filter(Download.created_at < cutoff_time).all()
        
        for download in old_downloads:
            try:
                if os.path.exists(download.filename):
                    os.remove(download.filename)
                db.session.delete(download)
            except Exception as e:
                logger.error(f"Cleanup error for {download.filename}: {str(e)}")
        
        db.session.commit()

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_old_files, 'interval', minutes=CLEANUP_INTERVAL)
scheduler.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-formats', methods=['POST'])
def get_formats():
    data = request.get_json()
    url = data.get("url")
    
    if not url or not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL"}), 400
    
    try:
        formats = get_available_formats(url)
        return jsonify({"formats": formats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    youtube_url = data.get("url")
    media_type = data.get("media_type", "audio")
    quality = data.get("quality", "mp3")
    
    if not youtube_url or not is_valid_youtube_url(youtube_url):
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        result = download_media(youtube_url, media_type, quality)
        return jsonify({"message": result})
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
