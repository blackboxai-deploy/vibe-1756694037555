#!/usr/bin/env python3
"""
API Client for Sound to Text Converter
Example client for interacting with the Flask web service API.
"""

import requests
import json
import os
import time
from pathlib import Path

class SoundToTextClient:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self):
        """Check if the API is healthy"""
        try:
            response = self.session.get(f'{self.base_url}/health')
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'status': 'unhealthy'}
    
    def transcribe_file(self, file_path, engine='google', language='en-US', chunk_duration=30):
        """
        Transcribe an audio file using the web API
        
        Args:
            file_path (str): Path to the audio file
            engine (str): Recognition engine ('google', 'sphinx', 'wit', 'bing')
            language (str): Language code (e.g., 'en-US', 'es-ES')
            chunk_duration (int): Chunk duration in seconds for long files
        
        Returns:
            dict: Transcription result or error
        """
        if not os.path.exists(file_path):
            return {'error': f'File not found: {file_path}'}
        
        # Prepare file upload
        file_name = Path(file_path).name
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f, self._get_mime_type(file_path))}
                data = {
                    'engine': engine,
                    'language': language,
                    'chunk_duration': str(chunk_duration)
                }
                
                print(f"Uploading {file_name}...")
                response = self.session.post(
                    f'{self.base_url}/upload',
                    files=files,
                    data=data,
                    timeout=300  # 5 minute timeout
                )
                
                response.raise_for_status()
                return response.json()
                
        except requests.exceptions.RequestException as e:
            return {'error': f'Request failed: {str(e)}'}
        except Exception as e:
            return {'error': f'Unexpected error: {str(e)}'}
    
    def get_result(self, result_filename):
        """Get a previously saved transcription result"""
        try:
            response = self.session.get(f'{self.base_url}/results/{result_filename}')
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def _get_mime_type(self, file_path):
        """Get MIME type for file"""
        extension = Path(file_path).suffix.lower()
        mime_types = {
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg',
            '.flac': 'audio/flac',
            '.m4a': 'audio/mp4',
            '.aac': 'audio/aac',
            '.ogg': 'audio/ogg',
            '.mp4': 'video/mp4'
        }
        return mime_types.get(extension, 'application/octet-stream')

def main():
    """Example usage of the API client"""
    client = SoundToTextClient()
    
    print("🎵 Sound to Text API Client")
    print("=" * 40)
    
    # Health check
    print("Checking API health...")
    health = client.health_check()
    if 'error' in health:
        print(f"❌ API is not available: {health['error']}")
        print("Make sure the Flask server is running: python app.py")
        return
    
    print("✅ API is healthy")
    print(f"Supported engines: {', '.join(health.get('supported_engines', []))}")
    print(f"Supported formats: {', '.join(health.get('supported_formats', []))}")
    print()
    
    # Interactive mode
    while True:
        print("\nOptions:")
        print("1. Transcribe audio file")
        print("2. Get saved result")
        print("3. Batch transcribe directory")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            transcribe_single_file(client)
        elif choice == '2':
            get_saved_result(client)
        elif choice == '3':
            batch_transcribe(client)
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")

def transcribe_single_file(client):
    """Transcribe a single audio file"""
    file_path = input("Enter path to audio file: ").strip()
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    # Get options
    print("\nTranscription options:")
    engine = input("Engine (google/sphinx/wit/bing) [google]: ").strip() or 'google'
    language = input("Language (en-US/es-ES/fr-FR/etc.) [en-US]: ").strip() or 'en-US'
    chunk_duration = input("Chunk duration for long files (seconds) [30]: ").strip()
    chunk_duration = int(chunk_duration) if chunk_duration.isdigit() else 30
    
    print(f"\n🔄 Transcribing {Path(file_path).name}...")
    start_time = time.time()
    
    result = client.transcribe_file(file_path, engine, language, chunk_duration)
    
    end_time = time.time()
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return
    
    if result.get('success'):
        transcription = result['result']
        print(f"\n✅ Transcription completed in {end_time - start_time:.1f} seconds")
        print("=" * 50)
        print("📝 TRANSCRIPTION:")
        print("=" * 50)
        print(transcription['text'])
        print("=" * 50)
        print(f"📊 Word count: {transcription.get('word_count', 0)}")
        print(f"⏱️ Duration: {transcription.get('duration', 0):.1f} seconds")
        print(f"🔧 Engine: {transcription.get('engine', 'unknown')}")
        print(f"🌐 Language: {transcription.get('language', 'unknown')}")
        
        # Save option
        save = input("\nSave to file? (y/n): ").strip().lower()
        if save == 'y':
            filename = input("Enter filename (e.g., transcript.txt): ").strip()
            if filename:
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(transcription['text'])
                    print(f"✅ Saved to {filename}")
                except Exception as e:
                    print(f"❌ Error saving file: {e}")
    else:
        print(f"❌ Transcription failed: {result.get('error', 'Unknown error')}")

def get_saved_result(client):
    """Retrieve a previously saved result"""
    result_filename = input("Enter result filename: ").strip()
    
    print(f"🔄 Fetching result {result_filename}...")
    result = client.get_result(result_filename)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print("✅ Result found:")
    print("=" * 50)
    print("📝 TRANSCRIPTION:")
    print("=" * 50)
    print(result.get('text', 'No text available'))
    print("=" * 50)
    print(f"📊 Word count: {result.get('word_count', 0)}")
    print(f"⏱️ Duration: {result.get('duration', 0):.1f} seconds")
    print(f"🔧 Engine: {result.get('engine', 'unknown')}")
    print(f"🌐 Language: {result.get('language', 'unknown')}")

def batch_transcribe(client):
    """Transcribe all audio files in a directory"""
    directory = input("Enter directory path: ").strip()
    
    if not os.path.isdir(directory):
        print(f"❌ Directory not found: {directory}")
        return
    
    # Find audio files
    audio_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.aac', '.ogg', '.mp4']
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(Path(directory).glob(f'*{ext}'))
        audio_files.extend(Path(directory).glob(f'*{ext.upper()}'))
    
    if not audio_files:
        print(f"❌ No audio files found in {directory}")
        return
    
    print(f"Found {len(audio_files)} audio files")
    
    # Get options
    engine = input("Engine (google/sphinx/wit/bing) [google]: ").strip() or 'google'
    language = input("Language (en-US/es-ES/fr-FR/etc.) [en-US]: ").strip() or 'en-US'
    
    # Process files
    results = []
    for i, file_path in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] Processing {file_path.name}...")
        
        result = client.transcribe_file(str(file_path), engine, language)
        
        if result.get('success'):
            transcription = result['result']
            print(f"✅ Success: {transcription.get('word_count', 0)} words")
            results.append({
                'file': file_path.name,
                'status': 'success',
                'text': transcription['text'],
                'word_count': transcription.get('word_count', 0)
            })
            
            # Save individual transcript
            transcript_file = file_path.with_suffix('.txt')
            try:
                with open(transcript_file, 'w', encoding='utf-8') as f:
                    f.write(transcription['text'])
                print(f"📁 Saved to {transcript_file}")
            except Exception as e:
                print(f"⚠️ Could not save {transcript_file}: {e}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            results.append({
                'file': file_path.name,
                'status': 'error',
                'error': result.get('error', 'Unknown error')
            })
    
    # Summary
    successful = len([r for r in results if r['status'] == 'success'])
    total_words = sum(r.get('word_count', 0) for r in results if r['status'] == 'success')
    
    print(f"\n📊 BATCH SUMMARY:")
    print(f"Total files: {len(audio_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(audio_files) - successful}")
    print(f"Total words transcribed: {total_words}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")