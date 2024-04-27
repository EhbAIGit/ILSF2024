import pygame
import time

# Initialiseer pygame en de joystick
pygame.init()
pygame.joystick.init()

# Controleer of er joysticks zijn aangesloten
if pygame.joystick.get_count() == 0:
    print("Geen joystick gevonden.")
    quit()

# Maak een lijst van alle aangesloten joysticks
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

# Initialiseer elke joystick
for joystick in joysticks:
    joystick.init()

try:
    while True:
        pygame.event.pump()

        # Lees de invoer van elke joystick uit
        for i, joystick in enumerate(joysticks):
            x_axis = joystick.get_axis(0)  # X-as
            y_axis = joystick.get_axis(1)  # Y-as
            z_axis = joystick.get_axis(2)  # Z-as (Trust)
            Buttons = [joystick.get_button(j) for j in range(joystick.get_numbuttons())]

            # Print de joystickgegevens
            print(f"Joystick {i}: X-as: {x_axis:.2f}, Y-as: {y_axis:.2f}, Z-as (Trust): {z_axis:.2f}, Buttons: {Buttons}")
        time.sleep(1)

except KeyboardInterrupt:
    print("Programma gestopt door gebruiker.")
