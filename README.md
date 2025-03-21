# YouTube Downloader

A Flask-based web application that enables users to download audio and video content from YouTube in various formats and quality levels. Built with modern web technologies, it provides a seamless experience for downloading and converting YouTube content.

## 🌟 Features

### Core Functionality
- ✅ **Audio Downloads**
  - MP3 format with quality options (128kbps, 192kbps, 320kbps)
  - WAV format for lossless audio
  - Automatic format conversion using pydub
- ✅ **Video Downloads**
  - Smart quality selection (4K, 1440p, 1080p, 720p, 480p, 360p)
  - Automatic quality adjustment based on available formats
  - Support for MP4 and MKV formats
- ✅ **User Interface**
  - Clean, modern design with Tailwind CSS
  - Mobile and desktop responsive
  - Real-time format checking
  - Progress indicators
  - Error feedback

### Technical Features
- ✅ **Performance**
  - Fast processing using yt-dlp
  - Efficient audio conversion with pydub
  - Background task scheduling with APScheduler
- ✅ **Security**
  - Input validation for YouTube URLs
  - File type verification
  - Temporary file management
- ✅ **Reliability**
  - Comprehensive error handling
  - Automatic file cleanup after 30 minutes
  - Download history tracking in SQLite

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask 3.0.2
- **YouTube Download**: yt-dlp 2024.3.10
- **Audio Processing**: pydub 0.25.1
- **Database**: SQLite with Flask-SQLAlchemy 3.1.1
- **Task Scheduling**: APScheduler 3.10.4

### Frontend
- **HTML5**: Semantic markup
- **CSS**: Tailwind CSS
- **JavaScript**: Modern ES6+
- **Icons**: Font Awesome

### Development Tools
- **Version Control**: Git
- **Environment Management**: Python venv
- **Package Management**: pip
- **Code Quality**: PEP 8

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- FFmpeg
- Git

### Step-by-Step Setup

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/youtube-downloader.git
cd youtube-downloader
```

2. **Set Up Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Install FFmpeg**
- **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html)
- **Linux**: `sudo apt-get install ffmpeg`
- **macOS**: `brew install ffmpeg`

5. **Run the Application**
```bash
python app.py
```

6. **Access the Application**
Open your browser and navigate to `http://localhost:5000`

## 🚀 Usage

### Basic Usage
1. Paste a YouTube URL in the search bar
2. Click "Check Formats" to see available formats
3. Select your desired format and quality
4. Click "Download" to start the download

### Advanced Features
- **Smart Quality Selection**: Automatically adjusts to best available quality
- **Format Options**: Choose between audio (MP3/WAV) and video formats
- **Download History**: Track your downloads in the SQLite database
- **Auto-Cleanup**: Files are automatically removed after 30 minutes

## 📁 Project Structure

```
youtube-downloader/
├── app.py                # Main Flask application
├── requirements.txt      # Python dependencies
├── static/              # Frontend assets
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   └── img/            # Images
├── templates/           # HTML templates
│   └── index.html      # Main page template
├── downloads/          # Temporary download directory
├── instance/          # SQLite database directory
├── .gitignore         # Git ignore rules
└── README.md          # Documentation
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
FLASK_ENV=development
FLASK_APP=app.py
MAX_DOWNLOAD_AGE=1800  # 30 minutes in seconds
```

### Customization Options
- Adjust download quality settings in `app.py`
- Modify file cleanup interval (default: 30 minutes)
- Configure error handling in the routes
- Customize UI themes in `templates/index.html`

## 🐛 Error Handling

The application handles various error scenarios:
- Invalid YouTube URLs (regex validation)
- Unsupported video formats
- Download failures
- Conversion errors
- File system errors
- Database errors
- Rate limiting

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube download functionality
- [pydub](https://github.com/jiaaro/pydub) for audio processing
- [Tailwind CSS](https://tailwindcss.com/) for styling
- [Font Awesome](https://fontawesome.com/) for icons

## 📞 Support

For support, please:
1. Check the [Issues](https://github.com/yourusername/youtube-downloader/issues) page
2. Create a new issue if needed
3. Join our [Discord community](https://discord.gg/your-server)

## 🔄 Updates

- **v1.0.0**: Initial release with basic download functionality
- **v1.1.0**: Added WAV format support and quality selection
- **v1.2.0**: Improved error handling and format detection
- **v1.3.0**: Added download history and auto-cleanup

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.
