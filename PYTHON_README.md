# Sound to Text Converter 🎵➡️📝

A comprehensive Python toolkit for converting audio files and recordings to text using speech recognition. Supports multiple audio formats, recognition engines, and processing modes.

## 🚀 Features

- **Multiple Input Sources**: Audio files, microphone recording, batch processing
- **Format Support**: WAV, MP3, M4A, FLAC, AAC, OGG, MP4
- **Recognition Engines**: Google Speech-to-Text, Sphinx, Wit.ai, Bing
- **Long Audio Processing**: Automatic chunking for files longer than 30 seconds
- **Batch Processing**: Process multiple files simultaneously
- **Output Formats**: Plain text, JSON with metadata
- **Interactive CLI**: User-friendly command-line interface

## 📦 Installation

### 1. Install Python Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Or install individually:
pip install SpeechRecognition pydub pyaudio pocketsphinx
```

### 2. Install System Dependencies

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install ffmpeg portaudio19-dev python3-pyaudio
```

#### On macOS:
```bash
brew install ffmpeg portaudio
pip install pyaudio
```

#### On Windows:
1. Download and install [FFmpeg](https://ffmpeg.org/download.html)
2. Add FFmpeg to your system PATH
3. Install PyAudio: `pip install pyaudio`

### 3. Optional: Setup API Keys

For advanced recognition engines, set environment variables:

```bash
# For Wit.ai
export WIT_AI_KEY="your_wit_ai_key"

# For Bing Speech Recognition
export BING_KEY="your_bing_key"
```

## 🎯 Quick Start

### Simple Example
```python
import speech_recognition as sr

# Initialize recognizer
r = sr.Recognizer()

# Transcribe audio file
with sr.AudioFile('audio.wav') as source:
    audio = r.record(source)
    text = r.recognize_google(audio)
    print(text)
```

### Using the Main Script
```bash
# Transcribe an audio file
python sound_to_text.py --file audio.wav

# Record and transcribe (5 seconds)
python sound_to_text.py --record 5

# Interactive mode
python sound_to_text.py
```

## 📖 Usage Examples

### 1. Basic File Transcription
```bash
# Transcribe a WAV file
python sound_to_text.py --file speech.wav

# Transcribe MP3 with Spanish language
python sound_to_text.py --file audio.mp3 --language es-ES

# Save output to file
python sound_to_text.py --file audio.wav --output transcript.txt
```

### 2. Microphone Recording
```bash
# Record for 10 seconds and transcribe
python sound_to_text.py --record 10

# Record with specific engine
python sound_to_text.py --record 5 --engine sphinx
```

### 3. Long Audio Processing
```bash
# Process long audio with chunking
python sound_to_text.py --file long_lecture.mp3 --long

# Custom chunk size (60 seconds)
python sound_to_text.py --file podcast.wav --long --chunk-size 60
```

### 4. Batch Processing
```bash
# Process all audio files in a directory
python batch_transcribe.py /path/to/audio/files

# Specify output directory
python batch_transcribe.py /audio/files --output /transcripts

# Use offline recognition
python batch_transcribe.py /audio/files --engine sphinx
```

### 5. Different Output Formats
```bash
# Save as JSON with metadata
python sound_to_text.py --file audio.wav --output result.json --format json

# The JSON includes:
# - transcript text
# - timestamp
# - word count
# - processing metadata
```

## 🛠️ Scripts Overview

### 1. `sound_to_text.py` - Main Converter
- **Purpose**: Comprehensive audio-to-text conversion
- **Features**: File transcription, recording, long audio processing
- **Usage**: Command-line arguments or interactive mode

### 2. `simple_example.py` - Basic Example
- **Purpose**: Simple demonstration of core functionality
- **Features**: Basic file transcription and microphone recording
- **Usage**: Educational and testing purposes

### 3. `batch_transcribe.py` - Batch Processor
- **Purpose**: Process multiple audio files simultaneously
- **Features**: Directory processing, progress tracking, detailed reporting
- **Usage**: Bulk transcription workflows

## 🎛️ Configuration Options

### Recognition Engines
- **Google** (default): Free, accurate, requires internet
- **Sphinx**: Offline, fast, less accurate
- **Wit.ai**: Good accuracy, requires API key
- **Bing**: Microsoft's service, requires API key

### Language Support
Common language codes:
- `en-US` - English (US)
- `en-GB` - English (UK)
- `es-ES` - Spanish (Spain)
- `fr-FR` - French (France)
- `de-DE` - German (Germany)
- `it-IT` - Italian (Italy)
- `pt-BR` - Portuguese (Brazil)
- `ru-RU` - Russian
- `ja-JP` - Japanese
- `zh-CN` - Chinese (Simplified)

### Audio Format Support
| Format | Extension | Notes |
|--------|-----------|--------|
| WAV | `.wav` | Best compatibility |
| MP3 | `.mp3` | Most common format |
| FLAC | `.flac` | Lossless quality |
| M4A | `.m4a` | Apple format |
| AAC | `.aac` | Good compression |
| OGG | `.ogg` | Open source |
| MP4 | `.mp4` | Video with audio |

## 💡 Tips for Better Results

### Audio Quality
1. **Clear Recording**: Minimize background noise
2. **Good Microphone**: Use quality recording equipment
3. **Proper Levels**: Avoid clipping and low volume
4. **Single Speaker**: Best results with one person speaking

### File Preparation
1. **Format**: WAV files work best for processing
2. **Sample Rate**: 16kHz or 44.1kHz recommended
3. **Mono Audio**: Convert stereo to mono if possible
4. **Noise Reduction**: Pre-process to remove background noise

### Processing Options
1. **Chunking**: Use `--long` flag for files > 30 seconds
2. **Language**: Specify correct language for better accuracy
3. **Engine Choice**: Try different engines for best results
4. **Ambient Noise**: Script automatically adjusts for background noise

## 🔧 Troubleshooting

### Common Issues

**"No module named 'pyaudio'"**
```bash
# Ubuntu/Debian
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio

# macOS
brew install portaudio
pip install pyaudio

# Windows
pip install pipwin
pipwin install pyaudio
```

**"Could not understand audio"**
- Check audio quality and volume
- Try different recognition engines
- Ensure correct language setting
- Verify audio file isn't corrupted

**"Request error" with Google API**
- Check internet connection
- API might be temporarily unavailable
- Try sphinx engine for offline processing

**FFmpeg not found**
- Install FFmpeg system-wide
- Add to PATH environment variable
- Verify installation: `ffmpeg -version`

### Performance Optimization

1. **For Large Batches**: Use batch processing script
2. **For Long Files**: Enable chunking with appropriate chunk size
3. **For Real-time**: Use microphone recording with shorter durations
4. **For Accuracy**: Use Google engine with good internet connection

## 📝 Example Output

### Text Format
```
Hello, this is a test of the speech recognition system. 
The weather today is quite nice and I hope this transcription works well.
```

### JSON Format
```json
{
  "transcript": "Hello, this is a test of the speech recognition system.",
  "timestamp": "2024-01-15 10:30:45",
  "word_count": 12,
  "processing_time": 2.34,
  "confidence": 0.95
}
```

### Batch Results
```json
{
  "processed": 5,
  "successful": 4,
  "failed": 1,
  "total_words": 1250,
  "processing_time": "2024-01-15 10:35:22",
  "results": [...]
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section
2. Verify all dependencies are installed correctly
3. Test with a simple WAV file first
4. Check internet connection for online engines

---

**Happy Transcribing! 🎵➡️📝**