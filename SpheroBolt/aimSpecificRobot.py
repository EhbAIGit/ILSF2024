import keyboard
from spherov2.sphero_edu import SpheroEduAPI
from spherov2 import scanner
from spherov2.types import Color

# Replace 'SPECIFIC_MAC_ADDRESS' with the MAC address of your Sphero Bolt
specific_mac_address = 'EB:C9:20:08:1D:86'

# Zoek en verbind met de Sphero robot met het opgegeven MAC-adres
toy = scanner.find_toy(mac=specific_mac_address)

if toy is None:
    print(f"Unable to find the Sphero Bolt with MAC address {specific_mac_address}. Make sure it's powered on and in pairing mode.")
else:
    with SpheroEduAPI(toy) as droid:
        heading = 0
        droid.set_back_led(Color(0, 255, 0))

        print("Druk op de pijltjestoetsen om de Sphero te richten. Druk op 'q' om af te sluiten.")

        while True:
            # Verhoog de richting met 10 graden als de rechter pijltjestoets wordt ingedrukt
            if keyboard.is_pressed('right'):
                heading += 10
                heading = heading % 360  # Zorg ervoor dat de waarde tussen 0 en 359 blijft
                droid.set_heading(heading)
                print(f"Richting: {heading} graden")
                while keyboard.is_pressed('right'):
                    pass  # Wacht tot de toets wordt losgelaten

            # Verlaag de richting met 10 graden als de linker pijltjestoets wordt ingedrukt
            elif keyboard.is_pressed('left'):
                heading -= 10
                heading = heading % 360
                droid.set_heading(heading)
                print(f"Richting: {heading} graden")
                while keyboard.is_pressed('left'):
                    pass

            # Stop het programma als 'q' wordt ingedrukt
            elif keyboard.is_pressed('q'):
                print("Programma afgesloten.")
                break