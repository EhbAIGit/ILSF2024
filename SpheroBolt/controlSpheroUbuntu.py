from pynput import keyboard
from spherov2.sphero_edu import SpheroEduAPI
from spherov2 import scanner
from spherov2.types import Color
import time

# Zoek en verbind met de Sphero robot
toy = scanner.find_toy(toy_name='SB-1D86')
with SpheroEduAPI(toy) as droid:
    print("Gebruik de pijltjestoetsen om te bewegen. Druk op 'q' om af te sluiten.")
    droid.set_back_led(Color(255, 0, 0))
    droid.set_matrix_fill(0, 0, 7, 7, Color(0, 255, 255))
    droid.roll(0, 60, 0.2)  # Richting 0 graden, snelheid 60, duur 2 seconden

    def on_press(key):
        try:
            if key.char == 'q':  # Stop het programma
                print("Programma afgesloten.")
                return False  # Stop listener
            if key == keyboard.Key.up:  # Vooruit bewegen
                droid.roll(0, 60, 0.2)
            elif key == keyboard.Key.down:  # Achteruit bewegen
                droid.roll(180, 60, 0.2)
            elif key == keyboard.Key.left:  # Naar links bewegen
                droid.roll(270, 60, 0.2)
            elif key == keyboard.Key.right:  # Naar rechts bewegen
                droid.roll(90, 60, 0.2)
        except AttributeError:
            pass

    # Luister naar toetsenbordaanslagen
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

    # Optioneel: Stop de beweging als er geen toets wordt ingedrukt
    droid.set_speed(0)
    time.sleep(0.1)  # Kleine pauze om CPU-gebruik te verminderen
