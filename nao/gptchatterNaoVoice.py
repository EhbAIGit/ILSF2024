import os
from openai import OpenAI
import numpy as np
import tempfile
from datetime import datetime, timezone, timedelta
import time
import warnings
warnings.filterwarnings("ignore")
import random
import paho.mqtt.client as mqtt
import re
import random
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize
import os
import yaml
#  speech to text
import sounddevice as sd
import tempfile
from scipy.io import wavfile
from scipy.io.wavfile import write

#from server_module import create_server_socket, accept_connection, receive_message, send_response, close_server_connection


# Define the MQTT server details
MQTT_BROKER = 'broker.emqx.io'  # Use the IP address or hostname of your MQTT broker
MQTT_PORT = 1883  # Default MQTT port is 1883 (use 8883 for SSL connections)
MQTT_TOPIC = 'NAO/SAY'
MQTT_MESSAGE = 'Hallo, Ik ben online!'

messageEnded = True

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Once connected, publish your message
    #client.publish(MQTT_TOPIC, MQTT_MESSAGE)

def on_publish(client, userdata, mid):
    print("Message Published.")


def on_message(client, userdata, msg):
    print("Message Received  "+msg.topic+":"+str(msg.payload))
    naofile = open("nao.txt",'w')
    naofile.write("DONE")
    naofile.close()
    return True


client_id = f'python-mqtt-{random.randint(0, 1000)}'
nao = mqtt.Client(client_id)

# Assign event callbacks
nao.on_connect = on_connect
nao.on_publish = on_publish
nao.on_message = on_message

# Connect to the MQTT broker
nao.connect(MQTT_BROKER, MQTT_PORT, 60)

nao.subscribe('NAO/DONE')

speakWithNao = True
keyfile = open("openaikey.txt",'r')
OPENAI_KEY = keyfile.read()

# start  Speech to text

def rms(frame):
    """
    Bereken de root mean square van de audio frame.
    """
    return np.sqrt(np.mean(np.square(frame), axis=0))

def record_until_silence(threshold=0.015, fs=44100, chunk_size=1024, max_silence=5):
    """
    Neemt audio op zolang er geluid is boven een bepaalde drempelwaarde en stopt na een bepaalde periode van stilte.
    :param threshold: De drempelwaarde voor het volume om te stoppen met opnemen.
    :param fs: Samplefrequentie.
    :param chunk_size: Het aantal samples per frame.
    :param max_silence: Maximale tijd in seconden om te wachten tijdens stilte voordat de opname stopt.
    :return: Pad naar het opgeslagen audiobestand.
    """
    print("Begin met opnemen... Spreek nu.")
    recorded_frames = []
    silent_frames = 5
    silence_limit = int(max_silence * fs / chunk_size)  # Aantal frames van stilte voordat opname stopt
    recording_started = False

    def callback(indata, frames, time, status):
        nonlocal silent_frames, recording_started
        volume_norm = rms(indata)
        if volume_norm < threshold:
            silent_frames += 1
            if silent_frames > silence_limit:
                raise sd.CallbackStop
        else:
            silent_frames = 0
            recording_started =  True
        
        recorded_frames.append(indata.copy())

    with sd.InputStream(callback=callback, device=1, dtype='float32', channels=1, samplerate=fs, blocksize=chunk_size):
        print("Opname gestart. Wacht op geluid...")
        sd.sleep(5000)  # Wacht maximaal 10 seconden voor geluid


    if (recording_started == False ) :
        print("\nGeen vraag waargenomen.")
        return 0
    else:
        print("Einde van de opname. Even geduld aub.")
        recording = np.concatenate(recorded_frames, axis=0)
        # Tijdelijk bestand aanmaken en opname opslaan
        temp_file = tempfile.mktemp(prefix='opgenomen_audio_', suffix='.wav')
        write(temp_file, fs, recording)  # Schrijf de opname naar een WAV-bestand

        #print(f"Audio opgenomen en opgeslagen in: {temp_file}")
        return temp_file


# end Speech to text




# PARSER METHODS

speech_controls = True
# default_contextual = False
default_contextual = True

def load_gestures():
    df = pd.read_csv('./nao/gestures_dataset/gestures.csv', usecols=['Category', 'Gesture', 'Weight'])

    global mappings
    mappings = {}

    # Group by the 'Category' and aggregate lists of 'Gesture' and 'Weight'
    for category, group in df.groupby('Category'):
        gestures = group['Gesture'].tolist()
        weights = group['Weight'].tolist()
        mappings[category] = (gestures, weights)   
    return mappings

def tokenize_sentences(text):
    # Download the Punkt tokenizer models (only needs to be done once)
    nltk.download('punkt')

    # Use NLTK's sent_tokenize to split text into sentences
    sentences = sent_tokenize(text)
    return sentences

def get_random_choice(gesture):
    global speech_controls, default_contextual
    pause = 1000
    speed = 80  # between 70-80 for an effective communication
    volume = 100 # maximum volume; range 10-100
    
    # We need Nao to hesitate one second after starting each gesture for an effective communication
    pause_marker =  f"\\pau={pause}\\"
    
    if speech_controls:   
        # Slow down Nao's speed and boost its volume for an effective communication 
        speech_controls_markers = f"\\rspd={speed}\\ \\vol={volume}\\"

    if not default_contextual:
        mode_marker = "^mode(disabled)"
    else:
        mode_marker = ""
    if gesture in mappings:
        choices, weights = mappings[gesture]
        selected_choice = random.choices(choices, weights)[0]
        return f"{speech_controls_markers} ^start(animations/Stand/Gestures/{selected_choice}) {pause_marker} {mode_marker}"
    
def replace_bracket_contents(text):
    pattern = r'\{([^}]+)\}'
    
    def replacement(match):
        gesture = match.group(1)  # Extract the gesture within the braces
        return get_random_choice(gesture)

    # Replace all occurrences in the text using the replacement function
    replaced_text = re.sub(pattern, replacement, text)
    return replaced_text

def save_parsed_text(text, directory='parsed_texts'):
    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    # List all files in the directory that match the naming pattern
    files = [f for f in os.listdir(directory) if f.startswith('parsed_text') and f.endswith('.txt')]
    
    # Sort files to find the highest numbered file
    files.sort()
    last_file = files[-1] if files else 'parsed_text0.txt'
    
    # Extract the number from the last file and increment it for the new file
    last_number = int(last_file.replace('parsed_text', '').replace('.txt', ''))
    new_file = f'parsed_text{last_number + 1}.txt'
    
    full_path = os.path.join(directory, new_file)
    
    with open(full_path, 'w') as file:
        file.write(text)

    print(f'File saved as {new_file}')

class CustomLoader(yaml.SafeLoader):
    def construct_scalar(self, node):
        value = super(CustomLoader, self).construct_scalar(node)
        return value.replace('\\\\', '\\')

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.load(file, Loader=CustomLoader)

load_gestures()

# End Parser Methods

client = OpenAI(api_key=OPENAI_KEY)

# Initial system message to set the context for the chat

# Open het tekstbestand in leesmodus ('r')
with open('nao/context.txt', 'r') as file:
    # Lees de inhoud van het bestand en sla het op in een string
    inhoud = file.read()



initial_messages = [
    {"role": "system", "content": inhoud},
]

# Initialize messages list with the initial system message
messages = initial_messages.copy()

firstCall = True
start_time = time.perf_counter()  # Precieze starttijd
toWait = 0

while True:
    # Ask user for input
    # Opname starten

    if (firstCall != True) :
        user_input = input("Press enter to speak")

        audio_file_path = record_until_silence()
        
        
        if (audio_file_path == 0) :
            continue


        #start_time = time.perf_counter()  # Precieze starttijd
        #subprocess.Popen(['python', 'playmp3.py', 'waiting\zeerLangWachten.mp3'])
        #toWait = 5


        with open(audio_file_path, "rb") as audio_file:
            user_input = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
            )
        # Check if the user wants to exit the chat
        user_input = user_input.text
    else :
        firstCall = False
        user_input = "Ok, now I ask a question, and you produce an answer with these gestures in braces. Speak normal English."


    if user_input.lower() == 'exit':
        print("Exiting chat...")
        break

    messages.append({"role": "assistant", "content": user_input}) 

    # Plaats hier de code waarvan je de uitvoeringstijd wilt meten

    # Generate a response from the model
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    end_time = time.perf_counter()  # Precieze eindtijd
    total_time = end_time - start_time


    print(f"Totale uitvoeringstijd voor chat: {total_time} seconden.")

    start_time = time.perf_counter() 


    naofile = open("nao.txt",'w')
    naofile.write("TALKING")
    naofile.close()

    if (speakWithNao == True) :
        
        sentences = tokenize_sentences(completion.choices[0].message.content)
        parsed_text = ""
        for sentence in sentences:
            parsed_sentence = replace_bracket_contents(sentence)
            parsed_text += parsed_sentence + "\n"
        print (parsed_text)
        nao.publish(MQTT_TOPIC, parsed_text)
    
    # Add model's response to the messages list to maintain context
    messages.append({"role": "assistant", "content": completion.choices[0].message.content})  # Corrected line
    
    if (speakWithNao == True) :
        nao.loop_start() #start the loop
        for i in range(30) :
            naofile = open("nao.txt",'r')
            naocontent = naofile.read()
            time.sleep(1)
            if (naocontent == "DONE" or 1==1 ) :
                print ("Nao Finished Talking")
                break
        nao.loop_stop() #stop the loop

    print (completion.choices[0].message.content)
