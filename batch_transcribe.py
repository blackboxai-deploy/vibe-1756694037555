#!/usr/bin/env python3
"""
Batch Audio Transcription Script
Process multiple audio files and save transcriptions.
"""

import speech_recognition as sr
import os
import glob
import json
import time
from pathlib import Path
import argparse

class BatchTranscriber:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.supported_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.mp4']
        self.results = []
    
    def transcribe_file(self, file_path, engine='google'):
        """Transcribe a single audio file"""
        print(f"Processing: {file_path}")
        
        try:
            # For non-WAV files, you'd need pydub conversion here
            with sr.AudioFile(file_path) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.record(source)
            
            if engine == 'google':
                text = self.recognizer.recognize_google(audio)
            elif engine == 'sphinx':
                text = self.recognizer.recognize_sphinx(audio)
            else:
                text = self.recognizer.recognize_google(audio)
            
            return {
                'file': file_path,
                'status': 'success',
                'transcription': text,
                'word_count': len(text.split()),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except sr.UnknownValueError:
            return {
                'file': file_path,
                'status': 'error',
                'error': 'Could not understand audio',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except sr.RequestError as e:
            return {
                'file': file_path,
                'status': 'error',
                'error': f'Service error: {str(e)}',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {
                'file': file_path,
                'status': 'error',
                'error': f'Processing error: {str(e)}',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def process_directory(self, directory, output_dir=None, engine='google'):
        """Process all audio files in a directory"""
        if output_dir is None:
            output_dir = os.path.join(directory, 'transcriptions')
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Find all audio files
        audio_files = []
        for ext in self.supported_extensions:
            pattern = os.path.join(directory, f'*{ext}')
            audio_files.extend(glob.glob(pattern))
            pattern = os.path.join(directory, f'*{ext.upper()}')
            audio_files.extend(glob.glob(pattern))
        
        if not audio_files:
            print(f"No audio files found in {directory}")
            return
        
        print(f"Found {len(audio_files)} audio files")
        print("=" * 50)
        
        # Process each file
        for i, file_path in enumerate(audio_files, 1):
            print(f"\n[{i}/{len(audio_files)}] Processing: {os.path.basename(file_path)}")
            
            # Skip non-WAV files for this simple example
            if not file_path.lower().endswith('.wav'):
                print("  ⚠️  Skipping non-WAV file (conversion needed)")
                continue
            
            result = self.transcribe_file(file_path, engine)
            self.results.append(result)
            
            # Save individual transcript
            if result['status'] == 'success':
                base_name = Path(file_path).stem
                transcript_file = os.path.join(output_dir, f"{base_name}_transcript.txt")
                
                with open(transcript_file, 'w', encoding='utf-8') as f:
                    f.write(result['transcription'])
                
                print(f"  ✅ Success: {result['word_count']} words")
                print(f"  📁 Saved to: {transcript_file}")
            else:
                print(f"  ❌ Failed: {result['error']}")
            
            # Small delay to avoid API rate limits
            time.sleep(0.5)
        
        # Save batch results
        self.save_batch_results(output_dir)
        self.print_summary()
    
    def save_batch_results(self, output_dir):
        """Save batch processing results to JSON"""
        results_file = os.path.join(output_dir, 'batch_results.json')
        
        summary = {
            'processed': len(self.results),
            'successful': len([r for r in self.results if r['status'] == 'success']),
            'failed': len([r for r in self.results if r['status'] == 'error']),
            'total_words': sum(r.get('word_count', 0) for r in self.results),
            'processing_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': self.results
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Batch results saved to: {results_file}")
    
    def print_summary(self):
        """Print processing summary"""
        successful = len([r for r in self.results if r['status'] == 'success'])
        failed = len([r for r in self.results if r['status'] == 'error'])
        total_words = sum(r.get('word_count', 0) for r in self.results)
        
        print("\n" + "=" * 50)
        print("📈 BATCH PROCESSING SUMMARY")
        print("=" * 50)
        print(f"Total files processed: {len(self.results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total words transcribed: {total_words}")
        print(f"Success rate: {(successful/len(self.results)*100):.1f}%" if self.results else "0%")
        
        if failed > 0:
            print("\n❌ Failed files:")
            for result in self.results:
                if result['status'] == 'error':
                    print(f"  • {os.path.basename(result['file'])}: {result['error']}")

def main():
    parser = argparse.ArgumentParser(description='Batch transcribe audio files')
    parser.add_argument('directory', help='Directory containing audio files')
    parser.add_argument('--output', '-o', help='Output directory for transcripts')
    parser.add_argument('--engine', '-e', default='google', 
                       choices=['google', 'sphinx'],
                       help='Speech recognition engine')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a valid directory")
        return
    
    print("🎵 Batch Audio Transcriber")
    print("=" * 50)
    print(f"Input directory: {args.directory}")
    print(f"Recognition engine: {args.engine}")
    
    # Initialize and run batch transcriber
    transcriber = BatchTranscriber()
    transcriber.process_directory(args.directory, args.output, args.engine)

if __name__ == "__main__":
    main()