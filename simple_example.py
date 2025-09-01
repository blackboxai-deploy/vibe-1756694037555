#!/usr/bin/env python3
"""
Simple Sound to Text Example
A basic example showing how to use the speech recognition library.
"""

import speech_recognition as sr
import os

def simple_file_transcription(audio_file):
    """Simple function to transcribe an audio file"""
    # Initialize recognizer
    r = sr.Recognizer()
    
    # Load audio file
    try:
        with sr.AudioFile(audio_file) as source:
            print("Loading audio file...")
            # Adjust for ambient noise and record
            r.adjust_for_ambient_noise(source)
            audio = r.record(source)
            
        print("Transcribing audio...")
        # Use Google Speech Recognition (free)
        text = r.recognize_google(audio)
        
        print(f"Transcription: {text}")
        return text
        
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Error with Google Speech Recognition: {e}")
        return None
    except FileNotFoundError:
        print("Audio file not found")
        return None

def simple_microphone_recording():
    """Simple function to record from microphone and transcribe"""
    # Initialize recognizer
    r = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("Adjusting for ambient noise... Please wait.")
            r.adjust_for_ambient_noise(source, duration=2)
            
            print("Say something!")
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            
        print("Transcribing...")
        text = r.recognize_google(audio)
        
        print(f"You said: {text}")
        return text
        
    except sr.WaitTimeoutError:
        print("No speech detected")
        return None
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Error with Google Speech Recognition: {e}")
        return None

def main():
    print("Simple Sound to Text Converter")
    print("=" * 30)
    
    while True:
        print("\nChoose an option:")
        print("1. Record from microphone")
        print("2. Transcribe audio file")
        print("3. Exit")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            print("\n--- Microphone Recording ---")
            result = simple_microphone_recording()
            
        elif choice == '2':
            print("\n--- File Transcription ---")
            file_path = input("Enter path to audio file (WAV format recommended): ").strip()
            
            if os.path.exists(file_path):
                result = simple_file_transcription(file_path)
            else:
                print("File not found!")
                continue
                
        elif choice == '3':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice!")
            continue
        
        # Save result option
        if result:
            save = input("\nSave to file? (y/n): ").strip().lower()
            if save == 'y':
                filename = input("Enter filename (e.g., transcript.txt): ").strip()
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(result)
                    print(f"Saved to {filename}")
                except Exception as e:
                    print(f"Error saving file: {e}")

if __name__ == "__main__":
    main()