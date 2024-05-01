from openai import OpenAI
from pathlib import Path

import sounddevice as sd
import soundfile as sf
import yaml

with open("keys.yaml", "r") as file:
    keys = yaml.safe_load(file)

client = OpenAI(api_key=keys["api_key"])
personality = "You are a Xarm Robot that that speaks french, dutch and english. You reacts randomly in all the languages"
messages = [{"role" : "system", "content" : f"{personality}"}]


# Mapping of actions to responses in different languages
responses = {
    "ZOEKEN": {
        "NL": "He, je kunt beter rennen, ik ga je vangen",
        "FR": "Hé, tu ferais mieux de courir, je vais te attraper",
        "EN": "Hey, you better run, I'm gonna catch you"
    },
    "GEVONDEN": {
        "NL": "Ik heb je gevonden",
        "FR": "Je t'ai trouvé",
        "EN": "I found you"
    },
    "ACHTERVOLGEN": {
        "NL": "Ik zit je achterna",
        "FR": "Je te poursuis",
        "EN": "I'm chasing you"
    },
    "OPGENOMEN": {
        "NL": "Ik heb je gevangen",
        "FR": "Je t'ai attrapé",
        "EN": "I caught you"
    }
}



def generate_audio(text):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice="echo",
        input=text
    )
    response.stream_to_file(speech_file_path)
    audio_data,sample_rate = sf.read(speech_file_path)
    sd.play(audio_data,sample_rate)
    sd.wait()

def generate_text():
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5,  # Adjust this value to manipulate randomness
        max_tokens=100,  # Adjust this value to manipulate length
        frequency_penalty=0.5,  # Adjust this value to manipulate frequency of common words
        presence_penalty=0.5  # Adjust this value to manipulate presence of new words
    )
    print(response.choices[0].message.content)

    bot_response = response.choices[0].message.content
    messages.append({"role" : "assistant", "content" : f"{bot_response}"})
    return bot_response

def main():
    while True:
        user_input = input("Enter text: ")
        messages.append({"role" : "user", "content" : f"{user_input}"})
        bot_response = generate_text()
        generate_audio(bot_response)

if __name__ == "__main__":
    main()