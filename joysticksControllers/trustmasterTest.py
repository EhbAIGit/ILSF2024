import pygame

# Initialiseer pygame en de joystick
pygame.init()
pygame.joystick.init()

# Controleer of er joysticks zijn aangesloten
if pygame.joystick.get_count() == 0:
    print("Geen joystick gevonden.")
    quit()

# Selecteer de eerste joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

try:
    while True:
        pygame.event.pump()

        # Lees de invoer van de joystick uit
        x_axis = joystick.get_axis(0)  # X-as
        y_axis = joystick.get_axis(1)  # Y-as
        z_axis = joystick.get_axis(2)  # Z-as (Trust)
        Buttons = [joystick.get_button(0),joystick.get_button(1),joystick.get_button(2),joystick.get_button(3)]
        Thumb_x = joystick.get_hat(0)[0]
        Thumb_y = joystick.get_hat(0)[1]
        # Print de joystickgegevens
        print("X-as: {:.2f}, Y-as: {:.2f}, Z-as (Trust): {:.2f}, Button3:{}, Hat(x-y):{}-{}".format(x_axis, y_axis, z_axis,Buttons,Thumb_x, Thumb_y))

except KeyboardInterrupt:
    print("Programma gestopt door gebruiker.")
