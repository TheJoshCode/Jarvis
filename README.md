Local AI Assistant with Voice Interaction

Welcome to your own personal AI assistant inspired by Jarvis from Iron Man! This project enables you to interact with an AI using your voice, directly through your microphone, providing responses in text and speech. It runs entirely locally, leveraging LM Studio for AI model management and OpenAI for chat capabilities.

Features
Voice Interaction: Communicate with the AI using your microphone.
Text-to-Speech (TTS): Responses are spoken out loud using pyttsx3 for a natural interaction experience.
Local Operation: Runs entirely on your machine, no internet required once set up.
Flexible AI Model: Dynamically detects and uses the active LM Studio model for responses.
Requirements
Python 3.6+
LM Studio setup with a loaded model
pyttsx3 for TTS
SpeechRecognition for voice input
Installation
Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/ai-assistant.git
cd ai-assistant
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Configure LM Studio:

Install LM Studio and load a model.
Start the LM Studio server and note the port (default: 1234).
Usage
Start the assistant:

bash
Copy code
python assistant.py
Speak into your microphone to interact with the AI.

The AI will respond both in text and spoken form using TTS.

Example
python
Copy code
# Sample code snippet showing interaction
import pyttsx3
import speech_recognition as sr

# Initialize TTS engine
engine = pyttsx3.init()

# Initialize speech recognition
recognizer = sr.Recognizer()
microphone = sr.Microphone()

def get_voice_input():
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I did not understand that.")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""

def main():
    # Example usage of voice interaction
    while True:
        user_input = get_voice_input()
        # Process user input and generate AI response
        # Perform actions based on AI response
        engine.say("AI response text")
        engine.runAndWait()

if __name__ == "__main__":
    main()
License
This project is licensed under the MIT License - see the LICENSE file for details.
