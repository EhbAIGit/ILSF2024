import pygame
import time
import socket
from spherov2 import scanner
from spherov2.types import Color
from spherov2.sphero_edu import SpheroEduAPI, EventType
from spherov2.commands.power import Power


class SpheroController:
    def __init__(self, joystick, color,ball_number):
        self.toy = None
        self.speed = 30
        self.heading = 0
        self.base_heading = 0
        self.is_running = True
        self.calibration_mode = False
        self.joystick = joystick
        self.last_command_time = time.time()
        self.heading_reset_interval = 1
        self.last_heading_reset_time = time.time()
        self.threshold_accel_mag = 0.05
        self.collision_occurred = False
        self.color = color  # Store the color parameter
        self.previous_button = 1
        self.number = ball_number  # Assign the ball number
    
    def discover_toy(self, toy_name):
        try:
            self.toy = scanner.find_toy(toy_name=toy_name)
            print(f"Sphero toy '{toy_name}' discovered.")

                
        except Exception as e:
            print(f"Error discovering toy: {e}")

    def connect_toy(self):
        if self.toy is not None:
            try:
                return SpheroEduAPI(self.toy)
            except Exception as e:
                print(f"Error connecting to toy: {e}")
        else:
            print("No toy discovered. Please run discover_toy() first.")
            return None

    def move(self, api, heading, speed):
        api.set_heading(heading)
        api.set_speed(speed)

    def toggle_calibration_mode(self, api, Y):
        if not self.calibration_mode:
            self.enter_calibration_mode(api, Y)
        else:
            self.exit_calibration_mode(api)

    def enter_calibration_mode(self, api, X):
        api.set_speed(0)
        print("Calibration mode activated.")
        self.calibration_mode = True
        api.set_front_led(Color(255, 0, 0))

        # Get the current heading angle
        self.base_heading = api.get_heading()

        # Determine the new heading based on Y value
        if X < -0.7:
            new_heading = self.base_heading + 5  # Turn +5 degrees
        elif X > 0.7:
            new_heading = self.base_heading - 5  # Turn -5 degrees
        else:
            new_heading = self.base_heading

        # Rotate the Sphero to the new heading
        api.set_heading(new_heading)

    def exit_calibration_mode(self, api):
        print("Exiting calibration mode.")
        self.calibration_mode = False
        api.set_front_led(Color(0, 255, 0))

    # Define LED patterns for each number
    LED_PATTERNS = {
        1: '1',
        2: '2',
        3: '3',
        4: '4'
    }


    # Method to set LED pattern for a specific number
    def set_number(self, number):
        self.number = number

    # Method to display number on LED matrix
    def display_number(self, api):
        number_char = self.LED_PATTERNS.get(self.number)
        if number_char:
            api.set_matrix_character(number_char, self.color)

    def print_battery_level(self, api):
        battery_voltage = Power.get_battery_voltage(self.toy)
        print(battery_voltage)

    def control_toy(self):
        lower_than_negative_threshold_time = None
        higher_than_positive_threshold_time = None
        try:
            with self.connect_toy() as api:
                last_battery_print_time = time.time()  # Initialize the last battery print time

                while self.is_running:
                    pygame.event.pump()

                    current_time2 = time.time()
                    if current_time2 - last_battery_print_time >= 45:
                        self.print_battery_level(api)
                        last_battery_print_time = current_time2  # Update the last battery print time

                    acceleration_data = api.get_acceleration()
                    if acceleration_data is not None:
                        z_acceleration = acceleration_data['z']
                        x_acceleration = acceleration_data['x']
                        y_acceleration = acceleration_data['y']
                        if x_acceleration < -0.7:
                          
                            lower_than_negative_threshold_time = int(time.time())
                            #print("lower", lower_than_negative_threshold_time)
                        if x_acceleration > 0.7:
                            
                            higher_than_positive_threshold_time = int(time.time())
                            #print("higher", higher_than_positive_threshold_time)

                        if lower_than_negative_threshold_time is not None and higher_than_positive_threshold_time is not None:
                            time_difference = abs(higher_than_positive_threshold_time - lower_than_negative_threshold_time)
                            print(time_difference)
                            if time_difference <= 10:
                                print(f"Ball Name: {self.toy.name} was LIFTED UP")
                                lower_than_negative_threshold_time = None
                                higher_than_positive_threshold_time = None
                            

                    else:
                        print("Acceleration data is not available.")
                    X = self.joystick.get_axis(0)
                    Y = self.joystick.get_axis(1)
                    button_x = self.joystick.get_button(0)  # Assuming X button is at index 0
                    if button_x == 0 and self.previous_button == 1:
                        self.toggle_calibration_mode(api, X)  # Pass Y value to toggle_calibration_mode
                    self.previous_button = button_x 

                    if self.calibration_mode:
                        self.enter_calibration_mode(api, X)  # Call enter_calibration_mode with Y value
                    else:
                        # Your movement logic based on joystick axes here
                        if Y < -0.7:
                            self.move(api, self.base_heading, self.speed)  # Left
                        elif Y > 0.7:
                            self.move(api, self.base_heading + 180, self.speed)  # Right
                        elif X > 0.7:
                            self.move(api, self.base_heading + 90, self.speed)  # Up
                        elif X < -0.7:
                            self.move(api, self.base_heading + 270, self.speed)  # Down
                        else:
                            api.set_speed(0)  # Stop


                    self.set_number(self.number)
                    self.display_number(api)

        finally:
            pygame.quit()  # Make sure to quit pygame when done



def main():
    # Initialize pygame and joysticks
    pygame.init()
    pygame.joystick.init()

    # Check for connected joysticks
    num_joysticks = pygame.joystick.get_count()
    if num_joysticks == 0:
        print("No joysticks found.")
        return

    # Define colors for each Sphero
    sphero_colors = [
        Color(255, 0, 0),   # Red
        Color(0, 255, 0),   # Green
        Color(0, 0, 255),   # Blue
        Color(255, 255, 0)  # Yellow
    ]

    # Create SpheroController instances and associate with joysticks
    sphero_controllers = []
    for i in range(num_joysticks):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        color = sphero_colors[i] if i < len(sphero_colors) else Color(255, 255, 255)  # Default to white if not enough colors
        sphero_controller = SpheroController(joystick, color, i + 1)
        sphero_controllers.append(sphero_controller)

    # Discover and connect to Sphero balls
    for sphero_controller in sphero_controllers:
        toy_name = input(f"Enter the toy name you want to connect to (for joystick {sphero_controller.joystick.get_id()}): ")
        sphero_controller.discover_toy(toy_name)
        if sphero_controller.toy:
            sphero_controller.control_toy()


if __name__ == "__main__":
    main()
