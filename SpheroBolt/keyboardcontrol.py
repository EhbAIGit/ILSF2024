import keyboard
from spherov2.sphero_edu import SpheroEduAPI
from spherov2 import scanner
import time

# Zoek en verbind met de Sphero robot
toy = scanner.find_toy(toy_name='SB-B72B')
with SpheroEduAPI(toy) as droid:
    print("Gebruik de pijltjestoetsen om te bewegen. Druk op 'q' om af te sluiten.")

    while True:
        if keyboard.is_pressed('up'):  # Vooruit bewegen
            droid.roll(0, 60, 0.2)  # Richting 0 graden, snelheid 60, duur 2 seconden
        elif keyboard.is_pressed('down'):  # Achteruit bewegen
            droid.roll(180, 60, 0.2)  # Richting 180 graden, snelheid 60, duur 2 seconden
        elif keyboard.is_pressed('left'):  # Naar links bewegen
            droid.roll(270, 60, 0.2)  # Richting 270 graden, snelheid 60, duur 2 seconden
        elif keyboard.is_pressed('right'):  # Naar rechts bewegen
            droid.roll(90, 60, 0.2)  # Richting 90 graden, snelheid 60, duur 2 seconden
        elif keyboard.is_pressed('q'):  # Stop het programma
            print("Programma afgesloten.")
            break

        #droid.set_speed(0)  # Stop de beweging als er geen toets wordt ingedrukt
        time.sleep(0.1)  # Kleine pauze om CPU-gebruik te verminderen
