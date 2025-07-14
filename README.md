# Jarvis

## A Fully On-Device Voice Assistant with STT, A VLM for image+text processing, and life-like TTS with XTTS-V2 voice cloning.

## Built to emulate Jarvis from the MCU Iron-Man series.

Prerequisites
Python: 3.11
- OS: Linux/Windows (macOS may require adjustments)
- Hardware: Microphone and speakers

# Installation

## 1. Clone this repository:
```bash
git clone https://github.com/TheJoshCode/jarvis.git
cd jarvis
```

## 2. Install:
```bash
install.bat
```

- NOTE: Ensure Jarvis.wav is in the project directory for voice cloning.
## 3. Run:

```bash
python jarvis.py
```

# Usage
- Start: Launch the script; Jarvis prompts you to press Enter to speak or type 'exit' to quit.
- Interact: Press Enter, speak into your microphone, and JARVIS responds with a cloned voice.
- Exit: Type "exit" to shut down gracefully.
- Interrupt: Press Ctrl+C to stop the script.

# Dependencies
- sqlite3: Manages chat history storage.
- pyaudio: Handles audio input/output.
- wave: Processes WAV files.
- faster_whisper: Provides fast speech-to-text transcription.
- ollama: Runs the gemma3:4b model for natural language processing.
- Chatterbox-TTS: Powers text-to-speech for voice cloning.

# How It Works
- Database: Initializes a SQLite database to store chat history for context-aware responses.
- Audio Input: Records audio via pyaudio and transcribes it using faster_whisper with int8 precision.
- Response Generation: Uses ollama with the gemma3:4b model, incorporating the last 5 interactions for context.
- Audio Output: Synthesizes JARVIS's response with xtts_v2 using a cloned voice from Jarvis.wav.
- Resource Management: Efficiently handles audio streams and temporary files.

# Contributing
- Pull requests are welcome! For major changes, please open an issue first to discuss.

# License
- MIT License - see LICENSE for details.

# Acknowledgments
- faster_whisper for efficient speech recognition: https://pypi.org/project/faster-whisper/1.1.1/
- ollama for seamless integration with gemma3:4b: https://ollama.com
- chatterbox-tts: https://github.com/resemble-ai/chatterbox

