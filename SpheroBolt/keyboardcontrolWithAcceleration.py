import keyboard
from spherov2.sphero_edu import SpheroEduAPI,Color,EventType
from spherov2 import scanner
from spherov2.commands.sensor import Sensor
import time


#add_collision_detected_notify_listener = partialmethod(Toy._add_listener, Sensor.collision_detected_notify)



# Zoek en verbind met de Sphero robot
toy = scanner.find_toy(toy_name='SB-1D86')
with SpheroEduAPI(toy) as droid:
    print("Gebruik de pijltjestoetsen om te bewegen. Druk op 'q' om af te sluiten.")

    def on_collision(api):
        print('Collision')
        time.sleep(10)

    def on_charging(api):
        print('charging')
        time.sleep(10)





    # Registreer de gebeurtenis voor botsingsdetectie
    droid.register_event(EventType.on_collision, on_collision)
    droid.register_event(EventType.on_charging, on_charging)

    # Variabelen voor het bijhouden van de vorige versnellingsgegevens
    prev_acceleration = (0, 0, 0)

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

        # Verkrijg en print versnellingsgegevens
        acceleration = droid.get_acceleration()
        if (acceleration['x'] > 0.8 or  acceleration['y'] > 0.9) :
             print ("Botsing gedetecteerd")
             distance = droid.get_distance()
             print("afgelegde afstand (cm):", distance)

        # Verkrijg de batterijstatus van de robot
        battery_percentage = Sensor.get

        # Druk de batterijstatus af
        print("Batterijpercentage:", battery_percentage)








        
        time.sleep(0.1)  # Kleine pauze om CPU-gebruik te verminderen
