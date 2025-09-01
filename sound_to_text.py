#!/usr/bin/env python3
"""
Sound to Text Converter
A comprehensive Python script for converting audio files to text using speech recognition.
Supports multiple audio formats and recognition engines.
"""

import speech_recognition as sr
import pydub
from pydub import AudioSegment
import os
import sys
import argparse
import json
from pathlib import Path
import time

class SoundToTextConverter:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.supported_formats = ['.wav', '.mp3', '.mp4', '.m4a', '.flac', '.aac', '.ogg']
        
    def convert_audio_format(self, input_file, output_format='wav'):
        """Convert audio file to specified format using pydub"""
        try:
            file_path = Path(input_file)
            file_extension = file_path.suffix.lower()
            
            print(f"Converting {file_extension} to {output_format}...")
            
            # Load audio file based on format
            if file_extension == '.mp3':
                audio = AudioSegment.from_mp3(input_file)
            elif file_extension == '.mp4' or file_extension == '.m4a':
                audio = AudioSegment.from_file(input_file, "mp4")
            elif file_extension == '.flac':
                audio = AudioSegment.from_flac(input_file)
            elif file_extension == '.ogg':
                audio = AudioSegment.from_ogg(input_file)
            elif file_extension == '.wav':
                audio = AudioSegment.from_wav(input_file)
            else:
                audio = AudioSegment.from_file(input_file)
            
            # Convert to wav for speech recognition
            output_file = f"temp_audio.{output_format}"
            audio.export(output_file, format=output_format)
            
            print(f"✓ Audio converted successfully to {output_format}")
            return output_file
            
        except Exception as e:
            print(f"✗ Error converting audio: {str(e)}")
            return None
    
    def transcribe_audio_file(self, audio_file, engine='google', language='en-US'):
        """Transcribe audio file to text using specified recognition engine"""
        try:
            # Convert to WAV if necessary
            file_extension = Path(audio_file).suffix.lower()
            if file_extension != '.wav':
                wav_file = self.convert_audio_format(audio_file, 'wav')
                if not wav_file:
                    return None
            else:
                wav_file = audio_file
            
            # Load audio file
            with sr.AudioFile(wav_file) as source:
                print("📁 Loading audio file...")
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio_data = self.recognizer.record(source)
                
            print(f"🎯 Transcribing using {engine} engine...")
            
            # Perform speech recognition
            if engine == 'google':
                text = self.recognizer.recognize_google(audio_data, language=language)
            elif engine == 'sphinx':
                text = self.recognizer.recognize_sphinx(audio_data)
            elif engine == 'wit':
                # Requires WIT_AI_KEY environment variable
                text = self.recognizer.recognize_wit(audio_data, key=os.getenv('WIT_AI_KEY'))
            elif engine == 'bing':
                # Requires BING_KEY environment variable
                text = self.recognizer.recognize_bing(audio_data, key=os.getenv('BING_KEY'), language=language)
            else:
                text = self.recognizer.recognize_google(audio_data, language=language)
            
            # Clean up temporary file
            if file_extension != '.wav' and os.path.exists('temp_audio.wav'):
                os.remove('temp_audio.wav')
                
            return text
            
        except sr.UnknownValueError:
            print("✗ Speech recognition could not understand the audio")
            return None
        except sr.RequestError as e:
            print(f"✗ Error with speech recognition service: {e}")
            return None
        except Exception as e:
            print(f"✗ Error during transcription: {str(e)}")
            return None
    
    def transcribe_long_audio(self, audio_file, chunk_length_ms=30000, engine='google', language='en-US'):
        """Transcribe long audio files by splitting into chunks"""
        try:
            # Load and convert audio
            file_extension = Path(audio_file).suffix.lower()
            if file_extension == '.wav':
                audio = AudioSegment.from_wav(audio_file)
            else:
                temp_wav = self.convert_audio_format(audio_file, 'wav')
                if not temp_wav:
                    return None
                audio = AudioSegment.from_wav(temp_wav)
            
            # Split audio into chunks
            chunks = []
            for i in range(0, len(audio), chunk_length_ms):
                chunk = audio[i:i + chunk_length_ms]
                chunks.append(chunk)
            
            print(f"📊 Processing {len(chunks)} audio chunks...")
            
            # Transcribe each chunk
            full_transcript = []
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{len(chunks)}...")
                
                # Export chunk to temporary file
                chunk_file = f"temp_chunk_{i}.wav"
                chunk.export(chunk_file, format="wav")
                
                # Transcribe chunk
                with sr.AudioFile(chunk_file) as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio_data = self.recognizer.record(source)
                
                try:
                    if engine == 'google':
                        text = self.recognizer.recognize_google(audio_data, language=language)
                    elif engine == 'sphinx':
                        text = self.recognizer.recognize_sphinx(audio_data)
                    else:
                        text = self.recognizer.recognize_google(audio_data, language=language)
                    
                    if text:
                        timestamp = f"[{i*chunk_length_ms//1000}s-{(i+1)*chunk_length_ms//1000}s]"
                        full_transcript.append(f"{timestamp} {text}")
                    
                except sr.UnknownValueError:
                    print(f"Could not understand chunk {i+1}")
                except sr.RequestError as e:
                    print(f"Error with chunk {i+1}: {e}")
                
                # Clean up chunk file
                if os.path.exists(chunk_file):
                    os.remove(chunk_file)
                
                # Small delay to avoid API rate limits
                time.sleep(0.1)
            
            # Clean up temporary wav file
            if file_extension != '.wav' and os.path.exists('temp_audio.wav'):
                os.remove('temp_audio.wav')
            
            return '\n'.join(full_transcript) if full_transcript else None
            
        except Exception as e:
            print(f"✗ Error during long audio transcription: {str(e)}")
            return None
    
    def record_and_transcribe(self, duration=5, engine='google', language='en-US'):
        """Record audio from microphone and transcribe"""
        try:
            with sr.Microphone() as source:
                print("🎤 Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                
                print(f"🔴 Recording for {duration} seconds...")
                audio_data = self.recognizer.listen(source, timeout=1, phrase_time_limit=duration)
                
                print("🎯 Transcribing recorded audio...")
                
                if engine == 'google':
                    text = self.recognizer.recognize_google(audio_data, language=language)
                elif engine == 'sphinx':
                    text = self.recognizer.recognize_sphinx(audio_data)
                else:
                    text = self.recognizer.recognize_google(audio_data, language=language)
                
                return text
                
        except sr.WaitTimeoutError:
            print("✗ No speech detected within timeout period")
            return None
        except sr.UnknownValueError:
            print("✗ Could not understand the recorded audio")
            return None
        except sr.RequestError as e:
            print(f"✗ Error with speech recognition service: {e}")
            return None
        except Exception as e:
            print(f"✗ Error during recording: {str(e)}")
            return None
    
    def save_transcript(self, text, output_file, format_type='txt'):
        """Save transcript to file in specified format"""
        try:
            if format_type == 'txt':
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(text)
            elif format_type == 'json':
                data = {
                    'transcript': text,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'word_count': len(text.split()) if text else 0
                }
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Transcript saved to {output_file}")
            return True
            
        except Exception as e:
            print(f"✗ Error saving transcript: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Convert sound to text using speech recognition')
    parser.add_argument('--file', '-f', help='Audio file path')
    parser.add_argument('--record', '-r', type=int, help='Record from microphone for specified seconds')
    parser.add_argument('--engine', '-e', default='google', 
                       choices=['google', 'sphinx', 'wit', 'bing'],
                       help='Speech recognition engine')
    parser.add_argument('--language', '-l', default='en-US', help='Language code (e.g., en-US, es-ES)')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', choices=['txt', 'json'], default='txt', help='Output format')
    parser.add_argument('--long', action='store_true', help='Use chunked processing for long audio files')
    parser.add_argument('--chunk-size', type=int, default=30, help='Chunk size in seconds for long audio')
    
    args = parser.parse_args()
    
    # Initialize converter
    converter = SoundToTextConverter()
    
    print("🎵 Sound to Text Converter")
    print("=" * 40)
    
    # Process based on arguments
    if args.file:
        # Transcribe audio file
        if not os.path.exists(args.file):
            print(f"✗ Error: File '{args.file}' not found")
            return
        
        print(f"📁 Processing file: {args.file}")
        
        if args.long:
            chunk_ms = args.chunk_size * 1000
            text = converter.transcribe_long_audio(args.file, chunk_ms, args.engine, args.language)
        else:
            text = converter.transcribe_audio_file(args.file, args.engine, args.language)
        
    elif args.record:
        # Record and transcribe
        text = converter.record_and_transcribe(args.record, args.engine, args.language)
        
    else:
        # Interactive mode
        print("\nSelect an option:")
        print("1. Transcribe audio file")
        print("2. Record and transcribe")
        
        choice = input("\nEnter choice (1-2): ").strip()
        
        if choice == '1':
            file_path = input("Enter audio file path: ").strip()
            if os.path.exists(file_path):
                is_long = input("Is this a long audio file? (y/n): ").strip().lower() == 'y'
                if is_long:
                    text = converter.transcribe_long_audio(file_path)
                else:
                    text = converter.transcribe_audio_file(file_path)
            else:
                print("✗ File not found")
                return
                
        elif choice == '2':
            duration = int(input("Enter recording duration in seconds (default 5): ") or 5)
            text = converter.record_and_transcribe(duration)
        
        else:
            print("✗ Invalid choice")
            return
    
    # Display and save results
    if text:
        print("\n" + "=" * 40)
        print("📝 TRANSCRIPTION RESULT:")
        print("=" * 40)
        print(text)
        print("=" * 40)
        
        # Save to file if specified
        if args.output:
            converter.save_transcript(text, args.output, args.format)
        else:
            # Ask if user wants to save
            save_choice = input("\nSave transcript to file? (y/n): ").strip().lower()
            if save_choice == 'y':
                output_file = input("Enter output filename: ").strip()
                if output_file:
                    converter.save_transcript(text, output_file, args.format)
    else:
        print("✗ No text could be extracted from the audio")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Process interrupted by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")