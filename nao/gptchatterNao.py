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

speakWithNao = False

OPENAI_KEY = 'put your key here'

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
        user_input = input("Your message: ")
    else :
        firstCall = False
        user_input = "Het spel is gestart"


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
        nao.publish(MQTT_TOPIC, completion.choices[0].message.content)
    
    # Add model's response to the messages list to maintain context
    messages.append({"role": "assistant", "content": completion.choices[0].message.content})  # Corrected line
    
    if (speakWithNao == True) :
        nao.loop_start() #start the loop
        for i in range(30) :
            naofile = open("nao.txt",'r')
            naocontent = naofile.read()
            time.sleep(1)
            if (naocontent == "DONE" ) :
                print ("Nao Finished Talking")
                break
        nao.loop_stop() #stop the loop

    print (completion.choices[0].message.content)
