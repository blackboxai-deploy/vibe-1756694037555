# 🎵 Sound to Text Web Application

A modern, full-featured web application for converting audio files and recordings to text using advanced speech recognition. Built with Flask and featuring a beautiful, responsive interface.

![Sound to Text Web App](https://placehold.co/800x400?text=Sound+to+Text+Web+Application+Interface)

## 🚀 Features

### 🎯 Core Functionality
- **File Upload**: Drag-and-drop or browse to upload audio files
- **Live Recording**: Record directly from microphone in the browser
- **Multiple Formats**: Support for WAV, MP3, FLAC, M4A, AAC, OGG, MP4
- **Batch Processing**: Process multiple files simultaneously
- **Real-time Progress**: Live processing feedback and progress indicators

### 🔧 Advanced Options
- **Multiple Engines**: Google (online), Sphinx (offline), Wit.ai, Bing
- **Language Support**: 10+ languages with automatic detection
- **Chunked Processing**: Smart splitting for long audio files
- **Quality Control**: Confidence scoring and error handling

### 💻 Modern Interface
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Intuitive UI**: Clean, modern interface with smooth animations
- **Real-time Feedback**: Progress indicators and status updates
- **Export Options**: Download as TXT, JSON, or copy to clipboard

### 🔒 Enterprise Ready
- **Production Deployment**: Gunicorn-based production server
- **API Endpoints**: RESTful API for integration
- **Logging & Monitoring**: Comprehensive logging and health checks
- **Security**: File validation, size limits, and secure uploads

## 📦 Installation

### 1. System Dependencies

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv ffmpeg portaudio19-dev
```

#### macOS:
```bash
brew install python3 ffmpeg portaudio
```

#### Windows:
1. Install Python 3.8+ from [python.org](https://python.org)
2. Download and install [FFmpeg](https://ffmpeg.org/download.html)
3. Add FFmpeg to your system PATH

### 2. Application Setup

```bash
# Clone or download the application files
git clone <repository-url>
cd sound-to-text-web

# Install Python dependencies
pip install -r web_requirements.txt

# Or use the deployment script (recommended)
python deploy.py deploy
```

## 🎯 Quick Start

### Development Mode
```bash
# Start development server
python app.py

# Access the application
open http://localhost:5000
```

### Production Deployment
```bash
# Full production deployment
python deploy.py deploy

# Or step by step:
python deploy.py start          # Start server
python deploy.py stop           # Stop server
python deploy.py restart        # Restart server
python deploy.py status         # Check status
```

### Custom Configuration
```bash
# Start on custom port with more workers
python deploy.py start 8080 8   # Port 8080, 8 workers
```

## 🌐 Web Interface Usage

### 1. File Upload Method
1. **Navigate** to the web interface at `http://localhost:5000`
2. **Choose "Upload File"** tab
3. **Drag and drop** your audio file or click "Choose File"
4. **Configure options**: Select engine, language, and chunk duration
5. **Wait for processing**: Progress indicator shows status
6. **View results**: Transcription appears with metadata
7. **Export**: Copy text, download TXT/JSON, or start new transcription

### 2. Live Recording Method
1. **Select "Record Audio"** tab
2. **Click "Start Recording"** (grant microphone permission if prompted)
3. **Speak clearly** into your microphone
4. **Click "Stop Recording"** when finished
5. **Processing** happens automatically
6. **View and export** your transcription

### 3. Advanced Options
- **Recognition Engine**: Choose between Google, Sphinx, Wit.ai, or Bing
- **Language**: Select from 10+ supported languages
- **Chunk Duration**: Adjust for optimal processing of long files
- **File Size**: Up to 100MB supported

## 📡 API Usage

### Health Check
```bash
curl http://localhost:5000/health
```

### File Upload API
```bash
curl -X POST http://localhost:5000/upload \
  -F "file=@audio.wav" \
  -F "engine=google" \
  -F "language=en-US" \
  -F "chunk_duration=30"
```

### Get Results
```bash
curl http://localhost:5000/results/20240115_143022_audio.wav.json
```

### Using the API Client
```python
from api_client import SoundToTextClient

client = SoundToTextClient('http://localhost:5000')

# Transcribe file
result = client.transcribe_file('audio.wav', engine='google', language='en-US')
print(result['result']['text'])

# Batch processing
client.batch_transcribe_directory('/path/to/audio/files')
```

## 🛠️ Configuration

### Environment Variables
```bash
# Optional API keys for advanced engines
export WIT_AI_KEY="your_wit_ai_key"
export BING_KEY="your_bing_speech_key"
```

### Application Settings
- **MAX_CONTENT_LENGTH**: 100MB (adjustable in app.py)
- **UPLOAD_FOLDER**: ./uploads (temporary file storage)
- **RESULTS_FOLDER**: ./results (transcription results)
- **SUPPORTED_FORMATS**: WAV, MP3, FLAC, M4A, AAC, OGG, MP4

### Production Configuration
```json
{
  "SECRET_KEY": "your-secret-key",
  "MAX_CONTENT_LENGTH": 104857600,
  "DEBUG": false,
  "WORKERS": 4,
  "PORT": 5000
}
```

## 📊 Performance & Scaling

### Processing Times
- **Short files** (< 30s): 2-5 seconds
- **Medium files** (1-5 min): 10-30 seconds  
- **Long files** (> 5 min): 1-3 minutes
- **Chunked processing**: Parallel processing for efficiency

### Scaling Options
```bash
# Increase workers for more concurrent processing
python deploy.py start 5000 8

# Deploy behind nginx for load balancing
# Configure nginx reverse proxy to Flask app
```

### Memory Usage
- **Base application**: ~50MB
- **Per file processing**: ~10-50MB depending on file size
- **Chunked processing**: Memory-efficient for large files

## 🔧 Troubleshooting

### Common Issues

**"Could not understand audio"**
- Check audio quality and clarity
- Ensure proper microphone setup
- Try different recognition engines
- Verify correct language selection

**"File upload failed"**
- Check file format (must be supported audio format)
- Verify file size (max 100MB)
- Ensure stable internet connection for online engines

**"Server not starting"**
- Verify all dependencies are installed
- Check port availability (5000 by default)
- Review error logs in `logs/error.log`
- Ensure FFmpeg is properly installed

**"Microphone not working"**
- Grant microphone permissions in browser
- Check browser compatibility (Chrome/Firefox recommended)
- Verify microphone hardware connection
- Test with other audio applications

### Debug Mode
```bash
# Run in debug mode for detailed error messages
FLASK_DEBUG=1 python app.py
```

### Logs and Monitoring
```bash
# Check server status
python deploy.py status

# View logs
tail -f logs/access.log
tail -f logs/error.log

# Health check
curl http://localhost:5000/health
```

## 🔒 Security Considerations

### File Validation
- **Format checking**: Only allowed audio formats accepted
- **Size limits**: 100MB maximum file size
- **Secure filenames**: Automatic sanitization of uploaded filenames
- **Temporary storage**: Files deleted after processing

### API Security
- **Input validation**: All parameters validated
- **Error handling**: No sensitive information in error messages
- **Rate limiting**: Consider implementing for production use
- **HTTPS**: Recommended for production deployment

### Production Deployment
- **Secret key**: Generate unique secret key for sessions
- **Environment variables**: Store API keys securely
- **Firewall**: Configure appropriate network security
- **Monitoring**: Set up log monitoring and alerts

## 📈 Monitoring & Analytics

### Built-in Monitoring
- **Health endpoint**: `/health` for uptime monitoring
- **Access logs**: Request logging with timestamps
- **Error logs**: Detailed error tracking
- **Processing metrics**: File size, duration, success rates

### Custom Monitoring
```python
# Add custom metrics collection
from datetime import datetime
import json

def log_transcription_metrics(result):
    metrics = {
        'timestamp': datetime.now().isoformat(),
        'duration': result['duration'],
        'word_count': result['word_count'],
        'engine': result['engine'],
        'success': True
    }
    
    with open('metrics.log', 'a') as f:
        f.write(json.dumps(metrics) + '\n')
```

## 🤝 Integration Examples

### Webhook Integration
```python
# Send results to webhook
import requests

def send_to_webhook(transcription_result):
    webhook_url = "https://your-api.com/webhook"
    payload = {
        'text': transcription_result['text'],
        'confidence': transcription_result['confidence'],
        'timestamp': transcription_result['timestamp']
    }
    
    requests.post(webhook_url, json=payload)
```

### Database Storage
```python
# Store results in database
import sqlite3

def store_transcription(result):
    conn = sqlite3.connect('transcriptions.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO transcriptions 
        (filename, text, word_count, engine, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        result['filename'],
        result['text'],
        result['word_count'],
        result['engine'],
        result['timestamp']
    ))
    
    conn.commit()
    conn.close()
```

## 🛡️ License & Support

### License
This project is open source and available under the [MIT License](LICENSE).

### Support
- **Documentation**: Check this README and code comments
- **Issues**: Report bugs and feature requests via GitHub issues
- **Community**: Join discussions and get help from the community
- **Professional Support**: Contact for enterprise support options

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

**Happy Transcribing! 🎵➡️📝**

*Built with ❤️ using Flask, SpeechRecognition, and modern web technologies*