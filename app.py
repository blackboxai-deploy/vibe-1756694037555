#!/usr/bin/env python3
"""
Web-based Sound to Text Converter
A Flask web application for converting audio files to text using speech recognition.
Supports file uploads, microphone recording, and real-time transcription.
"""

import os
import json
import time
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import speech_recognition as sr
from pydub import AudioSegment
from pathlib import Path
import tempfile
import shutil

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Enable CORS for cross-origin requests (useful for API usage)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'm4a', 'aac', 'ogg', 'mp4'}

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

class AudioTranscriber:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.supported_engines = {
            'google': self._recognize_google,
            'sphinx': self._recognize_sphinx,
            'wit': self._recognize_wit,
            'bing': self._recognize_bing
        }
    
    def _recognize_google(self, audio_data, language='en-US'):
        """Google Speech Recognition (free)"""
        return self.recognizer.recognize_google(audio_data, language=language)
    
    def _recognize_sphinx(self, audio_data, language='en-US'):
        """CMU Sphinx (offline)"""
        return self.recognizer.recognize_sphinx(audio_data)
    
    def _recognize_wit(self, audio_data, language='en-US'):
        """Wit.ai Recognition (requires API key)"""
        wit_key = os.getenv('WIT_AI_KEY')
        if not wit_key:
            raise Exception("WIT_AI_KEY environment variable not set")
        return self.recognizer.recognize_wit(audio_data, key=wit_key)
    
    def _recognize_bing(self, audio_data, language='en-US'):
        """Bing Speech Recognition (requires API key)"""
        bing_key = os.getenv('BING_KEY')
        if not bing_key:
            raise Exception("BING_KEY environment variable not set")
        return self.recognizer.recognize_bing(audio_data, key=bing_key, language=language)
    
    def convert_to_wav(self, input_file):
        """Convert audio file to WAV format"""
        try:
            file_path = Path(input_file)
            file_extension = file_path.suffix.lower()
            
            # Create temporary WAV file
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_wav_path = temp_wav.name
            temp_wav.close()
            
            # Load and convert audio based on format
            if file_extension == '.mp3':
                audio = AudioSegment.from_mp3(input_file)
            elif file_extension in ['.mp4', '.m4a']:
                audio = AudioSegment.from_file(input_file, "mp4")
            elif file_extension == '.flac':
                audio = AudioSegment.from_flac(input_file)
            elif file_extension == '.ogg':
                audio = AudioSegment.from_ogg(input_file)
            elif file_extension == '.aac':
                audio = AudioSegment.from_file(input_file, "aac")
            elif file_extension == '.wav':
                return input_file  # Already WAV
            else:
                audio = AudioSegment.from_file(input_file)
            
            # Export as WAV
            audio.export(temp_wav_path, format="wav")
            return temp_wav_path
            
        except Exception as e:
            raise Exception(f"Audio conversion failed: {str(e)}")
    
    def transcribe_audio(self, audio_file, engine='google', language='en-US', chunk_duration=30):
        """Transcribe audio file to text"""
        try:
            # Convert to WAV if necessary
            wav_file = self.convert_to_wav(audio_file)
            cleanup_wav = wav_file != audio_file
            
            # Load audio file
            with sr.AudioFile(wav_file) as source:
                # Get audio duration
                audio_segment = AudioSegment.from_wav(wav_file)
                duration_seconds = len(audio_segment) / 1000.0
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # For short files, transcribe directly
                if duration_seconds <= chunk_duration:
                    audio_data = self.recognizer.record(source)
                    text = self.supported_engines[engine](audio_data, language)
                    
                    result = {
                        'text': text,
                        'duration': duration_seconds,
                        'chunks': 1,
                        'word_count': len(text.split()) if text else 0,
                        'confidence': 'high'  # Placeholder
                    }
                else:
                    # For long files, process in chunks
                    result = self._transcribe_long_audio(wav_file, engine, language, chunk_duration)
            
            # Cleanup temporary WAV file
            if cleanup_wav and os.path.exists(wav_file):
                os.unlink(wav_file)
            
            return result
            
        except sr.UnknownValueError:
            raise Exception("Could not understand the audio")
        except sr.RequestError as e:
            raise Exception(f"Speech recognition service error: {str(e)}")
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    def _transcribe_long_audio(self, wav_file, engine, language, chunk_duration):
        """Transcribe long audio files in chunks"""
        audio = AudioSegment.from_wav(wav_file)
        chunk_length_ms = chunk_duration * 1000
        chunks = []
        full_transcript = []
        
        # Split audio into chunks
        for i in range(0, len(audio), chunk_length_ms):
            chunk = audio[i:i + chunk_length_ms]
            chunks.append(chunk)
        
        # Process each chunk
        successful_chunks = 0
        for i, chunk in enumerate(chunks):
            try:
                # Create temporary file for chunk
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_chunk:
                    chunk.export(temp_chunk.name, format="wav")
                    
                    # Transcribe chunk
                    with sr.AudioFile(temp_chunk.name) as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio_data = self.recognizer.record(source)
                        
                        text = self.supported_engines[engine](audio_data, language)
                        
                        if text.strip():
                            start_time = i * chunk_duration
                            end_time = min((i + 1) * chunk_duration, len(audio) / 1000)
                            
                            full_transcript.append({
                                'text': text.strip(),
                                'start_time': start_time,
                                'end_time': end_time
                            })
                            successful_chunks += 1
                    
                    # Cleanup chunk file
                    os.unlink(temp_chunk.name)
                    
            except Exception as e:
                print(f"Error processing chunk {i+1}: {str(e)}")
                continue
        
        # Combine all transcripts
        combined_text = ' '.join([chunk['text'] for chunk in full_transcript])
        
        return {
            'text': combined_text,
            'duration': len(audio) / 1000.0,
            'chunks': len(chunks),
            'successful_chunks': successful_chunks,
            'word_count': len(combined_text.split()) if combined_text else 0,
            'confidence': 'medium' if successful_chunks < len(chunks) else 'high',
            'detailed_chunks': full_transcript
        }

# Initialize transcriber
transcriber = AudioTranscriber()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_result(result, filename):
    """Save transcription result to file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_filename = f"{timestamp}_{filename}.json"
    result_path = os.path.join(RESULTS_FOLDER, result_filename)
    
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    return result_filename

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and transcription"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not supported. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Get transcription parameters
        engine = request.form.get('engine', 'google')
        language = request.form.get('language', 'en-US')
        chunk_duration = int(request.form.get('chunk_duration', 30))
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Transcribe audio
        start_time = time.time()
        result = transcriber.transcribe_audio(file_path, engine, language, chunk_duration)
        processing_time = time.time() - start_time
        
        # Add metadata
        result.update({
            'filename': filename,
            'engine': engine,
            'language': language,
            'processing_time': round(processing_time, 2),
            'timestamp': datetime.now().isoformat(),
            'file_size': os.path.getsize(file_path)
        })
        
        # Save result
        result_filename = save_result(result, filename)
        
        # Cleanup uploaded file
        os.unlink(file_path)
        
        return jsonify({
            'success': True,
            'result': result,
            'result_file': result_filename
        })
        
    except RequestEntityTooLarge:
        return jsonify({'error': 'File too large. Maximum size: 100MB'}), 413
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transcribe', methods=['POST'])
def api_transcribe():
    """API endpoint for transcription"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        # This would be used for base64 audio data or URLs
        # Implementation depends on your specific needs
        
        return jsonify({'message': 'API transcription endpoint - implement based on your needs'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results/<filename>')
def get_result(filename):
    """Get transcription result"""
    try:
        result_path = os.path.join(RESULTS_FOLDER, filename)
        if not os.path.exists(result_path):
            return jsonify({'error': 'Result not found'}), 404
        
        with open(result_path, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'supported_engines': list(transcriber.supported_engines.keys()),
        'supported_formats': list(ALLOWED_EXTENSIONS)
    })

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size: 100MB'}), 413

@app.errorhandler(500)
def server_error(e):
    """Handle server errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🎵 Sound to Text Web Converter")
    print("=" * 40)
    print("Starting Flask web server...")
    print("Access the application at: http://localhost:5000")
    print("API endpoint: http://localhost:5000/api/transcribe")
    print("Health check: http://localhost:5000/health")
    print("=" * 40)
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )