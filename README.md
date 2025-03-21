# YouTube Downloader

A full-stack web application that allows users to download audio and video from YouTube in multiple formats and quality levels.

## Features

- ✅ Download Audio & Video: Support MP3, WAV, MP4, MKV, and more
- ✅ Quality Selection: Choose from different quality levels (128kbps, 320kbps for audio; 720p, 1080p, 4K for video)
- ✅ User-Friendly UI: Clean interface with a search bar for pasting YouTube links
- ✅ Fast Processing: Uses yt-dlp for efficient downloads and pydub for audio conversion
- ✅ Temporary File Storage: Auto-deletes downloaded files after 30 minutes
- ✅ Error Handling: Proper error messages for invalid links or unsupported formats
- ✅ Mobile & Desktop Responsive: Works smoothly on all devices

## Tech Stack

- Backend: Flask (Python) + yt-dlp + pydub
- Frontend: HTML, Tailwind CSS, JavaScript
- Database: SQLite (for download history tracking)
- Dependencies: See requirements.txt

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Pineapple4623/youtube-downloader.git
cd youtube-downloader
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install FFmpeg (required for audio processing):
- Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html)
- Linux: `sudo apt-get install ffmpeg`
- macOS: `brew install ffmpeg`

5. Run the application:
```bash
python app.py
```

6. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Paste a YouTube URL in the search bar
2. Click "Check Formats" to see available formats
3. Select your desired format and quality
4. Click "Download" to start the download

## Project Structure

```
youtube-downloader/
│── app.py                # Main Flask backend
│── requirements.txt      # Dependencies
│── static/              # Frontend assets
│── templates/           # HTML files
│   ├── index.html       # Main frontend
│── downloads/           # Temporary folder for downloads
│── .gitignore          # Ignore unnecessary files
│── README.md           # Documentation
```

## Features in Detail

### Audio Downloads
- MP3 format with quality options (128kbps, 192kbps, 320kbps)
- WAV format for lossless audio
- Automatic format conversion using pydub

### Video Downloads
- Multiple quality options (480p, 720p, 1080p, 4K)
- Support for MP4 and MKV formats
- Best quality selection based on available formats

### File Management
- Automatic file cleanup after 30 minutes
- Unique filenames using timestamps
- Download history tracking in SQLite database

## Error Handling

The application handles various error cases:
- Invalid YouTube URLs
- Unsupported video formats
- Download failures
- Conversion errors
- File system errors

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube download functionality
- [pydub](https://github.com/jiaaro/pydub) for audio processing
- [Tailwind CSS](https://tailwindcss.com/) for styling
- [Font Awesome](https://fontawesome.com/) for icons
