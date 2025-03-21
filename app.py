from flask import Flask, request, send_file, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import yt_dlp
from pydub import AudioSegment
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
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')
CLEANUP_INTERVAL = 30  # minutes
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
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            
            # Get video duration
            duration = info.get('duration', 0)
            duration_str = f"{duration//60}:{duration%60:02d}" if duration else "Unknown"
            
            # Audio formats
            audio_formats = [f for f in info['formats'] if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            if audio_formats:
                formats.append({
                    'type': 'audio',
                    'formats': [
                        {'id': 'mp3_320', 'name': 'MP3 320kbps'},
                        {'id': 'mp3_192', 'name': 'MP3 192kbps'},
                        {'id': 'mp3_128', 'name': 'MP3 128kbps'},
                        {'id': 'wav', 'name': 'WAV (Lossless)'}
                    ]
                })
            
            # Video formats
            video_formats = [f for f in info['formats'] if f.get('vcodec') != 'none']
            if video_formats:
                # Get available heights and their format IDs
                available_heights = {}
                for f in video_formats:
                    height = f.get('height')
                    if height and height > 0:
                        if height not in available_heights:
                            available_heights[height] = []
                        available_heights[height].append(f.get('format_id'))
                
                # Sort heights in descending order
                sorted_heights = sorted(available_heights.keys(), reverse=True)
                
                # Map available heights to quality options
                quality_options = []
                
                # Add best quality option first
                quality_options.append({'id': 'best', 'name': 'Best Available Quality'})
                
                # Add specific quality options based on available heights
                for height in sorted_heights:
                    if height >= 2160:
                        quality_options.append({'id': '4k', 'name': f'4K ({height}p)'})
                    elif height >= 1440:
                        quality_options.append({'id': '1440p', 'name': f'1440p ({height}p)'})
                    elif height >= 1080:
                        quality_options.append({'id': '1080p', 'name': f'1080p ({height}p)'})
                    elif height >= 720:
                        quality_options.append({'id': '720p', 'name': f'720p ({height}p)'})
                    elif height >= 480:
                        quality_options.append({'id': '480p', 'name': f'480p ({height}p)'})
                    elif height >= 360:
                        quality_options.append({'id': '360p', 'name': f'360p ({height}p)'})
                
                formats.append({
                    'type': 'video',
                    'formats': quality_options,
                    'duration': duration_str,
                    'title': info.get('title', 'Unknown Title'),
                    'max_height': max(sorted_heights) if sorted_heights else 0
                })
            
            return formats
    except Exception as e:
        logger.error(f"Error getting formats: {str(e)}")
        return []

def download_media(youtube_url, media_type, quality):
    timestamp = int(time.time())
    if media_type == "audio":
        quality_map = {
            "mp3_320": "320",
            "mp3_192": "192",
            "mp3_128": "128",
            "wav": "wav"
        }
        selected_quality = quality_map.get(quality, "320")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'audio_{timestamp}.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': selected_quality,
            }],
            'quiet': True,
        }
        target_filename = os.path.join(DOWNLOAD_FOLDER, f'audio_{timestamp}.mp3')
    else:
        # First get the available formats to check if the requested quality is available
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            video_formats = [f for f in info['formats'] if f.get('vcodec') != 'none']
            available_heights = sorted(list(set(
                f.get('height', 0) for f in video_formats 
                if f.get('height') is not None and f.get('height') > 0
            )), reverse=True)
            
            max_height = max(available_heights) if available_heights else 0
            
            # Adjust quality based on available heights
            if quality == "4k" and max_height < 2160:
                quality = "1080p"
            elif quality == "1440p" and max_height < 1440:
                quality = "1080p"
            elif quality == "1080p" and max_height < 1080:
                quality = "720p"
            elif quality == "720p" and max_height < 720:
                quality = "480p"
            elif quality == "480p" and max_height < 480:
                quality = "360p"
            elif quality == "360p" and max_height < 360:
                quality = "best"
        
        quality_map = {
            "4k": "bestvideo[height>=2160]+bestaudio/best[height>=2160]",
            "1440p": "bestvideo[height>=1440]+bestaudio/best[height>=1440]",
            "1080p": "bestvideo[height>=1080]+bestaudio/best[height>=1080]",
            "720p": "bestvideo[height>=720]+bestaudio/best[height>=720]",
            "480p": "bestvideo[height>=480]+bestaudio/best[height>=480]",
            "360p": "bestvideo[height>=360]+bestaudio/best[height>=360]",
            "best": "bestvideo+bestaudio/best"
        }
        fmt = quality_map.get(quality, "bestvideo+bestaudio/best")
        
        ydl_opts = {
            'format': fmt,
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'video_{timestamp}.%(ext)s'),
            'quiet': True,
        }
        target_filename = None

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            if media_type == "video":
                ext = info_dict.get('ext', 'mp4')
                target_filename = os.path.join(DOWNLOAD_FOLDER, f"video_{timestamp}.{ext}")
            
            # Record download in database
            download = Download(
                filename=target_filename,
                format=media_type,
                quality=quality
            )
            db.session.add(download)
            db.session.commit()
            
            return target_filename
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        raise

def convert_audio_to_wav(mp3_file):
    wav_file = mp3_file.replace('.mp3', '.wav')
    try:
        audio = AudioSegment.from_mp3(mp3_file)
        audio.export(wav_file, format="wav")
        return wav_file
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
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
    quality = data.get("quality", "mp3_320")
    
    if not youtube_url or not is_valid_youtube_url(youtube_url):
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        file_path = download_media(youtube_url, media_type, quality)
        if media_type == "audio" and quality == "wav":
            file_path = convert_audio_to_wav(file_path)
        return send_file(file_path, as_attachment=True)
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
