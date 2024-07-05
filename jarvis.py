import openai
import pyttsx3
import speech_recognition as sr
import sys
import requests

# Initialize OpenAI client pointing to the local LMStudio server
client = openai.OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# Initialize the TTS engine
engine = pyttsx3.init()

# Initialize the speech recognition recognizer
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Function to get voice input from the user
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

# Function to fetch the active model ID from LMStudio
def get_active_model_id():
    try:
        # Fetch models list from LMStudio
        response = requests.get("http://localhost:1234/v1/models")
        models_data = response.json().get("data", [])

        # Find the first active model
        for model in models_data:
            if model.get("object") == "model":
                return model["id"]

        print("No active models found.")
        return None
    except Exception as e:
        print(f"Error fetching active model: {e}")
        return None

# Main loop for continuous conversation
while True:
    try:
        # Get the active model ID
        model_id = get_active_model_id()
        if not model_id:
            print("Exiting the chat.")
            break

        # Create a chat completion request using the active model
        completion = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "system", "content": "You are an intelligent assistant."}],
            temperature=0.5,
            stream=True,
        )

        # Initialize the new message for the assistant's response
        new_message = {"role": "assistant", "content": ""}
        
        # Stream and print the assistant's response
        for chunk in completion:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
                new_message["content"] += chunk.choices[0].delta.content

        # Append the assistant's response to the chat history
        print()
        
        # Use TTS to read out the assistant's response
        engine.say(new_message["content"])
        engine.runAndWait()

        # Get voice input from the user for the next message
        user_input = get_voice_input()
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chat.")
            break

        if user_input:
            history.append({"role": "user", "content": user_input})

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

# Uncomment to see chat history
# import json
# gray_color = "\033[90m"
# reset_color = "\033[0m"
# print(f"{gray_color}\n{'-'*20} History dump {'-'*20}\n")
# print(json.dumps(history, indent=2))
# print(f"\n{'-'*55}\n{reset_color}")
