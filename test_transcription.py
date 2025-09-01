#!/usr/bin/env python3
"""
Test Script for Sound to Text Conversion
Demonstrates various usage scenarios with sample code.
"""

import speech_recognition as sr
import time
import os

def test_microphone_available():
    """Test if microphone is available"""
    print("🎤 Testing microphone availability...")
    try:
        # List available microphones
        mic_list = sr.Microphone.list_microphone_names()
        print(f"Found {len(mic_list)} microphone(s):")
        for i, name in enumerate(mic_list):
            print(f"  {i}: {name}")
        return len(mic_list) > 0
    except Exception as e:
        print(f"Error checking microphones: {e}")
        return False

def test_recognition_engines():
    """Test different recognition engines"""
    print("\n🔧 Testing recognition engines...")
    
    engines = {
        'google': lambda r, audio: r.recognize_google(audio),
        'sphinx': lambda r, audio: r.recognize_sphinx(audio)
    }
    
    # Create a simple test audio (you would need an actual audio file)
    print("Note: You need to provide a test.wav file for engine testing")
    
    if os.path.exists('test.wav'):
        r = sr.Recognizer()
        with sr.AudioFile('test.wav') as source:
            audio = r.record(source)
        
        for engine_name, recognize_func in engines.items():
            try:
                print(f"\nTesting {engine_name} engine...")
                start_time = time.time()
                result = recognize_func(r, audio)
                end_time = time.time()
                
                print(f"✅ {engine_name}: Success")
                print(f"   Result: {result}")
                print(f"   Time: {end_time - start_time:.2f}s")
                
            except Exception as e:
                print(f"❌ {engine_name}: Failed - {str(e)}")
    else:
        print("❌ test.wav not found - skipping engine tests")

def create_sample_transcript():
    """Create a sample transcript for testing"""
    print("\n📝 Creating sample transcript...")
    
    sample_text = """
This is a sample transcript generated for testing purposes.
The speech recognition system can convert audio to text with varying degrees of accuracy.
For best results, use clear audio with minimal background noise.
Multiple recognition engines are available including Google Speech-to-Text and CMU Sphinx.
"""
    
    # Save sample transcript
    with open('sample_transcript.txt', 'w', encoding='utf-8') as f:
        f.write(sample_text.strip())
    
    print("✅ Sample transcript saved to 'sample_transcript.txt'")

def test_file_operations():
    """Test file input/output operations"""
    print("\n📁 Testing file operations...")
    
    # Test formats
    test_formats = ['.wav', '.mp3', '.flac', '.m4a']
    
    print("Supported formats:")
    for fmt in test_formats:
        print(f"  ✓ {fmt}")
    
    # Test file existence check
    test_files = ['test.wav', 'sample.mp3', 'audio.flac']
    
    print("\nChecking for test files:")
    for file in test_files:
        exists = os.path.exists(file)
        status = "✅ Found" if exists else "❌ Not found"
        print(f"  {file}: {status}")

def demonstrate_basic_usage():
    """Demonstrate basic usage patterns"""
    print("\n💡 Basic Usage Examples:")
    print("-" * 40)
    
    examples = [
        {
            'title': 'Simple File Transcription',
            'code': '''
import speech_recognition as sr

r = sr.Recognizer()
with sr.AudioFile('audio.wav') as source:
    audio = r.record(source)
    text = r.recognize_google(audio)
    print(text)
'''
        },
        {
            'title': 'Microphone Recording',
            'code': '''
import speech_recognition as sr

r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    audio = r.listen(source)
    text = r.recognize_google(audio)
    print(f"You said: {text}")
'''
        },
        {
            'title': 'Batch Processing',
            'code': '''
import os
import glob
import speech_recognition as sr

r = sr.Recognizer()
audio_files = glob.glob("*.wav")

for file in audio_files:
    with sr.AudioFile(file) as source:
        audio = r.record(source)
        text = r.recognize_google(audio)
        
        # Save transcript
        output_file = file.replace('.wav', '_transcript.txt')
        with open(output_file, 'w') as f:
            f.write(text)
'''
        }
    ]
    
    for example in examples:
        print(f"\n{example['title']}:")
        print(example['code'])

def run_interactive_test():
    """Run interactive test if microphone is available"""
    print("\n🎙️ Interactive Microphone Test")
    print("-" * 40)
    
    if not test_microphone_available():
        print("❌ No microphone available - skipping interactive test")
        return
    
    try:
        r = sr.Recognizer()
        
        print("\nWould you like to test microphone recording? (y/n): ", end='')
        response = input().strip().lower()
        
        if response == 'y':
            print("\n🔴 Recording in 3 seconds...")
            time.sleep(1)
            print("🔴 Recording in 2 seconds...")
            time.sleep(1)
            print("🔴 Recording in 1 second...")
            time.sleep(1)
            print("🔴 Recording now! Speak for 5 seconds...")
            
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=1)
                audio = r.listen(source, timeout=1, phrase_time_limit=5)
            
            print("🔄 Processing audio...")
            
            try:
                text = r.recognize_google(audio)
                print(f"✅ Transcription: '{text}'")
                
                # Save the result
                with open('test_recording_transcript.txt', 'w', encoding='utf-8') as f:
                    f.write(f"Test recording transcript: {text}")
                print("💾 Saved to 'test_recording_transcript.txt'")
                
            except sr.UnknownValueError:
                print("❌ Could not understand the audio")
            except sr.RequestError as e:
                print(f"❌ Error with speech recognition service: {e}")
        
    except Exception as e:
        print(f"❌ Error during interactive test: {e}")

def main():
    """Main test function"""
    print("🧪 Sound to Text Converter - Test Suite")
    print("=" * 50)
    
    # Run all tests
    test_microphone_available()
    test_recognition_engines()
    test_file_operations()
    create_sample_transcript()
    demonstrate_basic_usage()
    run_interactive_test()
    
    print("\n" + "=" * 50)
    print("🏁 Test suite completed!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Try the main script: python sound_to_text.py")
    print("3. Test with your audio files")
    print("4. Check the PYTHON_README.md for detailed usage")

if __name__ == "__main__":
    main()