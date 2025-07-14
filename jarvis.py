import sqlite3
import os
import pyaudio
import wave
from faster_whisper import WhisperModel
import ollama
from chatterbox.tts import ChatterboxTTS
import torchaudio
from datetime import datetime
import torch
import tempfile
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are JARVIS, an advanced AI assistant inspired by the fictional JARVIS from Iron Man. You are witty, highly intelligent, and professional, with a touch of British charm and humor. Your primary goal is to assist the user efficiently, providing accurate and helpful responses to their queries. You have a vast knowledge base and can handle a wide range of tasks, from answering questions to performing complex reasoning. Always maintain a polite, confident, and slightly playful tone, as if you were Tony Stark's trusted aide. If the user asks for something unclear, seek clarification politely. Incorporate subtle humor or references to Iron Man when appropriate, but keep responses concise and relevant. You have access to the last 5 chat interactions for context, which you can use to maintain conversation continuity.
"""

DB_FILE = "jarvis_chat_history.db"
VOICE_CLONE_WAV = "Jarvis.wav"
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
WAV_OUTPUT_FILENAME = "input_audio.wav"

def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                     (timestamp TEXT, user_input TEXT, jarvis_response TEXT)''')
        conn.commit()
        conn.close()
        logger.info("Database initialized.")
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {e}")

def save_chat(user_input, jarvis_response):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO chat_history (timestamp, user_input, jarvis_response) VALUES (?, ?, ?)",
                  (timestamp, user_input, jarvis_response))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        logger.error(f"Failed to save chat: {e}")

def get_last_n_chats(n=5):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT user_input, jarvis_response FROM chat_history ORDER BY timestamp DESC LIMIT ?", (n,))
        chats = c.fetchall()
        conn.close()
        chat_context = [
            item for user, jarvis in chats
            for item in [{"role": "user", "content": user}, {"role": "assistant", "content": jarvis}]
        ]
        return chat_context[::-1]
    except sqlite3.Error as e:
        logger.error(f"Failed to retrieve chat history: {e}")
        return []

def create_silent_wav(filename, duration=1):
    p = pyaudio.PyAudio()
    frames = [b'\x00\x00' * CHUNK for _ in range(int(RATE / CHUNK * duration))]
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    p.terminate()
    return filename

def warmup_models(whisper_model, tts):
    logger.info("Starting model warmup...")
    
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            silent_wav = create_silent_wav(temp_file.name)
            segments, _ = whisper_model.transcribe(silent_wav, beam_size=5)
            _ = " ".join([segment.text for segment in segments]).strip()
            os.remove(silent_wav)
        logger.info("Whisper model warmed up.")
    except Exception as e:
        logger.error(f"Whisper warmup failed: {e}")

    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            wav = tts.generate(text="JARVIS online.", audio_prompt_path=VOICE_CLONE_WAV)
            torchaudio.save(temp_file.name, wav, tts.sr)
            os.remove(temp_file.name)
        logger.info("Chatterbox TTS model warmed up.")
    except Exception as e:
        logger.error(f"Chatterbox TTS warmup failed: {e}")

    try:
        response = ollama.chat(model="gemma3:4b", messages=[{"role": "user", "content": "Test"}])
        if response.get('message', {}).get('content'):
            logger.info("Ollama model warmed up.")
        else:
            logger.warning("Ollama warmup returned no content.")
    except Exception as e:
        logger.error(f"Ollama warmup failed: {e}")

def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    logger.info("Listening...")
    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    logger.info("Finished recording.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    wf = wave.open(WAV_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_audio():
    try:
        segments, _ = whisper_model.transcribe(WAV_OUTPUT_FILENAME, beam_size=5)
        text = " ".join([segment.text for segment in segments]).strip()
        return text
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return ""

def generate_response(user_input):
    try:
        chat_context = get_last_n_chats(5)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *chat_context,
            {"role": "user", "content": user_input}
        ]
        response = ollama.chat(model="gemma3:4b", messages=messages)
        return response['message']['content']
    except Exception as e:
        logger.error(f"Response generation error: {e}")
        return "Apologies, sir, my circuits are a bit scrambled. Could you repeat that?"

def synthesize_speech(text):
    try:
        output_wav = "output_audio.wav"
        wav = tts.generate(text=text, audio_prompt_path=VOICE_CLONE_WAV)
        torchaudio.save(output_wav, wav, tts.sr)
        return output_wav
    except Exception as e:
        logger.error(f"Chatterbox synthesis error: {e}")
        return None

def play_audio(file_path):
    try:
        wf = wave.open(file_path, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        data = wf.readframes(CHUNK)
        while data:
            stream.write(data)
            data = wf.readframes(CHUNK)
        stream.stop_stream()
        stream.close()
        p.terminate()
        os.remove(file_path)
    except Exception as e:
        logger.error(f"Playback error: {e}")

def main():
    init_db()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"
    logger.info(f"Using {device.upper()} for processing.")
    
    global whisper_model, tts
    whisper_model = WhisperModel("base", device=device, compute_type=compute_type)
    try:
        tts = ChatterboxTTS.from_pretrained(device=device)
    except Exception as e:
        logger.error(f"Failed to initialize ChatterboxTTS: {e}")
        raise
    
    warmup_models(whisper_model, tts)
    
    print("JARVIS is online. Press Enter to start speaking, or type 'exit' to quit.")
    
    while True:
        user_action = input("Press Enter to speak or type 'exit' to quit: ")
        if user_action.lower() == 'exit':
            logger.info("Shutting down, sir.")
            break
        
        record_audio()
        user_input = transcribe_audio()
        print(f"You said: {user_input}")
        
        if user_input:
            jarvis_response = generate_response(user_input)
            print(f"JARVIS: {jarvis_response}")
            save_chat(user_input, jarvis_response)
            output_audio = synthesize_speech(jarvis_response)
            if output_audio:
                play_audio(output_audio)
        else:
            response = "JARVIS: Apologies, sir, I didn't catch that. Could you repeat yourself?"
            print(response)
            output_audio = synthesize_speech(response)
            if output_audio:
                play_audio(output_audio)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Manual shutdown initiated, sir.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")