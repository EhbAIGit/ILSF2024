import keyboard
import time

# Functie om de robot vooruit te bewegen
def vooruit():
    print("Robot gaat vooruit")

# Functie om de robot achteruit te bewegen
def achteruit():
    print("Robot gaat achteruit")

# Functie om de robot naar links te draaien
def links():
    print("Robot draait naar links")

# Functie om de robot naar rechts te draaien
def rechts():
    print("Robot draait naar rechts")

try:
    while True:
        if keyboard.is_pressed('w'):
            vooruit()
        elif keyboard.is_pressed('s'):
            achteruit()
        elif keyboard.is_pressed('a'):
            links()
        elif keyboard.is_pressed('d'):
            rechts()
        time.sleep(0.1)  # Wacht even om te voorkomen dat het programma te snel reageert
except KeyboardInterrupt:
    pass
