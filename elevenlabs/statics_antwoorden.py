from openai import OpenAI
from pathlib import Path
import sounddevice as sd
import soundfile as sf
import yaml
import random

# Laden van API-sleutels uit een YAML-bestand
with open("keys.yaml", "r") as file:
    keys = yaml.safe_load(file)

# Initialisatie van de OpenAI-client en definities van persoonlijkheid en berichten
client = OpenAI(api_key=keys["api_key"])
personality = "You are a Xarm Robot that speaks French, Dutch, and English. You react randomly in all languages."
messages = [{"role" : "system", "content" : f"{personality}"}]

# Vooraf gedefinieerde antwoorden per taal en actie
responses = {
    "SEARCHING": {
        "NL": [
            "He, je kunt beter rennen, ik ga je vangen",
            "Kom maar tevoorschijn, ik ga je vinden",
            "Ik ben op zoek naar jou, ren maar weg",
            "Waar ben je? Ik kom eraan!",
            "Je kunt niet voor me wegrennen, ik kom eraan",
            "Je kunt maar beter verstoppen, ik kom eraan",
            "Je kunt me niet ontlopen, ik ben op jacht",
            "Ik zal je vinden, hoe ver je ook gaat",
            "Waar verstop je je? Ik kom eraan",
            "Je kunt maar beter snel zijn, ik kom eraan"
        ],
        "FR": [
            "Hé, tu ferais mieux de courir, je vais te attraper",
            "Viens te montrer, je vais te trouver",
            "Je te cherche, enfuis-toi",
            "Où es-tu? J'arrive!",
            "Tu ne peux pas m'échapper, je suis en route",
            "Tu ferais mieux de te cacher, je suis en route",
            "Tu ne peux pas me fuir, je suis à la poursuite",
            "Je te trouverai, où que tu ailles",
            "Où te caches-tu? J'arrive",
            "Tu ferais mieux de te dépêcher, j'arrive"
        ],
        "EN": [
            "Hey, you better run, I'm gonna catch you!",
            "Come out, come out, wherever you are, I'm coming for you",
            "I'm on the hunt for you, so run away",
            "Where are you? I'm coming!",
            "You can't escape me, I'm on my way",
            "You better hide, I'm on my way",
            "You can't run from me, I'm in pursuit",
            "I'll find you, no matter where you go",
            "Where are you hiding? I'm coming",
            "You better hurry up, I'm coming"
        ]
    },
    "FOUND": {
        "NL": [
            "Ik heb je gevonden",
            "Daar ben je dan, ik heb je",
            "Je kunt niet voor me wegduiken, ik heb je gevonden",
            "Ik wist dat ik je zou vinden",
            "Ik heb je, geen ontsnappen meer aan",
            "Ik wist dat je ergens was, en hier ben je",
            "Er is geen ontsnappen meer aan, ik heb je gevonden",
            "Ik zag je daar, ik heb je",
            "Er is geen plek om te verstoppen, ik heb je gevonden",
            "Je kunt niet eeuwig wegrennen, ik heb je gevonden"
        ],
        "FR": [
            "Je t'ai trouvé",
            "Te voilà, je t'ai",
            "Tu ne peux pas te cacher de moi, je t'ai trouvé",
            "Je savais que je te trouverais",
            "Je t'ai, plus moyen de t'échapper",
            "Je savais que tu étais quelque part, et te voilà",
            "Il n'y a plus d'échappatoire, je t'ai trouvé",
            "Je t'ai vu là-bas, je t'ai",
            "Il n'y a pas d'endroit où te cacher, je t'ai trouvé",
            "Tu ne peux pas courir éternellement, je t'ai trouvé"
        ],
        "EN": [
            "I found you",
            "There you are, I found you",
            "You can't hide from me, I found you",
            "I knew I would find you",
            "I got you, no escaping now",
            "I knew you were somewhere, and here you are",
            "There's no getting away now, I found you",
            "I saw you over there, I found you",
            "There's nowhere to hide, I found you",
            "You can't run forever, I found you"
        ]
    },
    "PURSUE": {
        "NL": [
            "Ik zit je achterna",
            "Wacht maar, ik kom eraan",
            "Je kunt niet voor me wegrennen, ik ben achter je aan",
            "Ik blijf je volgen, waar je ook gaat",
            "Je kunt niet ontsnappen, ik ben je op de hielen",
            "Ik blijf je volgen, je kunt nergens heen",
            "Wacht maar, ik ga je inhalen",
            "Ik laat je niet ontsnappen, ik ben achter je aan",
            "Je kunt niet wegrennen van me, ik ben hier",
            "Ik blijf je volgen, totdat ik je heb"
        ],
        "FR": [
            "Je te poursuis",
            "Attends-moi, j'arrive",
            "Tu ne peux pas te cacher de moi, je te suis",
            "Je te suis, où que tu ailles",
            "Tu ne peux pas t'échapper, je suis à tes trousses",
            "Je te suis, tu ne peux nulle part aller",
            "Attends-moi, je vais te rattraper",
            "Je ne te laisserai pas t'échapper, je te suis",
            "Tu ne peux pas fuir, je suis là",
            "Je te suis, jusqu'à ce que je t'attrape"
        ],
        "EN": [
            "I'm chasing you",
            "Wait up, I'm coming",
            "You can't run away from me, I'm after you",
            "I'll follow you wherever you go",
            "You can't escape, I'm on your tail",
            "I'll follow you, you can't go anywhere",
            "Wait up, I'm gonna catch you",
            "I won't let you escape, I'm after you",
            "You can't run from me, I'm here",
            "I'll follow you until I catch you"
        ]
    },
    "CAUGHT": {
        "NL": [
            "Ik heb je gevangen",
            "Je kunt niet wegkomen, ik heb je",
            "Je kunt niet ontsnappen, je bent van mij",
            "Ik heb je, geen ontsnappen meer aan",
            "Je bent de mijne, geen ontsnappen meer",
            "Ik heb je te pakken, geen ontkomen aan",
            "Je bent gevangen, ik heb je",
            "Ik wist dat ik je zou vangen, en hier ben je",
            "Er is geen ontkomen aan, ik heb je gevangen",
            "Je kunt niet vluchten, ik heb je"
        ],
        "FR": [
            "Je t'ai attrapé",
            "Tu ne peux pas t'échapper, je t'ai",
            "Tu ne peux pas fuir, tu m'appartiens",
            "Je t'ai, plus moyen de t'échapper",
            "Tu es à moi, plus d'évasion possible",
            "Je t'ai attrapé, tu ne peux pas t'en sortir",
            "Tu es pris, je t'ai",
            "Je savais que je te prendrais, et te voilà",
            "Il n'y a pas d'échappatoire, je t'ai attrapé",
            "Tu ne peux pas t'enfuir, je t'ai"
        ],
        "EN": [
            "I caught you",
            "You can't get away, I got you",
            "You can't escape, you're mine",
            "I got you, no escaping now",
            "You're mine, no getting away now",
            "I got you, no escaping from me",
            "You're caught, I got you",
            "I knew I would catch you, and here you are",
            "There's no escaping now, I caught you",
            "You can't run, I caught you"
        ]
    }
}


# Functie om audio te genereren van een tekst
def generate_audio(text):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice="onyx",
        input=text
    )
    response.stream_to_file(speech_file_path)
    audio_data, sample_rate = sf.read(speech_file_path)
    sd.play(audio_data, sample_rate)
    sd.wait()

# Functie om een willekeurig bericht te genereren op basis van de acties en talen
def generate_text(action, language):
    return random.choice(responses[action][language])

# Hoofdfunctionaliteit om de gebruiker om invoer te vragen en vervolgens reacties te genereren
def main():
        while True:
            user_input = input("Enter text: ")
            if user_input in responses.keys():
                action = user_input # Convert input to uppercase
                language = random.choice(["NL", "FR", "EN"])  # Choose a random language
                bot_response = generate_text(action, language)  # Generate response
                messages.append({"role" : "user", "content" : f"{user_input}"})
                messages.append({"role" : "assistant", "content" : f"{bot_response}"})
                generate_audio(bot_response)


if __name__ == "__main__":
    main()

