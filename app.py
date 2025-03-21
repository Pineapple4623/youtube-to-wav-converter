from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import os
import time
import logging
from datetime import datetime, timedelta
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///downloads.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
API_BASE_URL = "https://loader.to/api"

class Download(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    url = db.Column(db.String(255), nullable=False)

with app.app_context():
    db.create_all()

def is_valid_youtube_url(url):
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^"&?/s]{11})'
    return bool(re.match(youtube_regex, url))

def get_card_iframe(url):
    try:
        # Generate the card iframe URL with the video URL
        iframe_url = f"{API_BASE_URL}/card/?url={url}"
        
        # Record the download attempt in database
        download = Download(url=url)
        db.session.add(download)
        db.session.commit()
        
        return iframe_url
    except Exception as e:
        logger.error(f"Error generating card iframe: {str(e)}")
        raise

def cleanup_old_files():
    with app.app_context():
        cutoff_time = datetime.utcnow() - timedelta(minutes=30)  # 30 minutes
        old_downloads = Download.query.filter(Download.created_at < cutoff_time).all()
        
        for download in old_downloads:
            try:
                db.session.delete(download)
            except Exception as e:
                logger.error(f"Cleanup error: {str(e)}")
        
        db.session.commit()

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_old_files, 'interval', minutes=30)
scheduler.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-card', methods=['POST'])
def get_card():
    data = request.get_json()
    youtube_url = data.get("url")
    
    if not youtube_url or not is_valid_youtube_url(youtube_url):
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        iframe_url = get_card_iframe(youtube_url)
        return jsonify({
            "iframe_url": iframe_url,
            "iframe_html": f'<iframe style="width:800px;height:250px;border:0;overflow:hidden;" scrolling="no" src="{iframe_url}"></iframe>'
        })
    except Exception as e:
        logger.error(f"Error getting card: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
