

# This script needs modified corrected spherov2 library (spherov2.zip).  Copy this to the python site-packages folder. 

# sphero_controller.py

import socket
from spherov2 import scanner
from spherov2.types import Color
from spherov2.sphero_edu import SpheroEduAPI, EventType
import time
import re  # Import the 're' module for regular expressions
from spherov2.types import Color
import struct
from spherov2.commands.power import Power

class SpheroController:
    def __init__(self):
        self.toy = None
        self.speed = 50
        self.heading = 0
        self.base_heading = 0  # Store the calibrated heading
        self.is_running = True
        self.calibration_mode = False
        self.previous_button = 1
        self.last_command_time = time.time()
        self.heading_reset_interval = 1
        self.last_heading_reset_time = time.time()
        self.threshold_accel_mag = 0.05  # Adjust this value for sensitivity
        self.collision_occurred = False  # Variable to track collision occurrence


    def discover_toy(self):
        try:
            self.toy = scanner.find_toy(toy_name="SB-2C26")
            print("Sphero toy discovered.")
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

    def enter_calibration_mode(self, api, Y):
        api.set_speed(0)
        print("Calibration mode activated.")
        self.calibration_mode = True
        api.set_front_led(Color(255, 0, 0))

        # Get the current heading angle
        self.base_heading = api.get_heading()

        # Determine the new heading based on Y value
        if Y < 300:
            new_heading = self.base_heading + 5  # Turn +5 degrees
        elif Y > 800:
            new_heading = self.base_heading - 5  # Turn -5 degrees
        else:
            new_heading = self.base_heading

        # Rotate the Sphero to the new heading
        api.set_heading(new_heading)


    def exit_calibration_mode(self, api):
        print("Exiting calibration mode.")
        self.calibration_mode = False
        api.set_front_led(Color(0, 255, 0))
    
    
        

    def control_toy(self):
        with self.connect_toy() as api:
            # Initialize the client socket
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 5555))

            #api.register_event(EventType.on_collision, self.detect_collision)
            last_battery_print_time = time.time()  # Initialize the last battery print time
            api.register_event(EventType.on_landing, self.detect_landing)
            api.register_event(EventType.on_collision, self.detect_collision)  # Register the freefall detection method

            

            while self.is_running:
                # Receive data from arduino.py
                data = client_socket.recv(1024).decode('utf-8')
                # self.detect_liftup(api)
                self.detect_freefall(api)
                current_time2 = time.time()
                if current_time2 - last_battery_print_time >= 45:
                    self.print_battery_level(api)
                    last_battery_print_time = current_time2  # Update the last battery print time

                
                # api.register_event(EventType.on_landing, self.detect_landing)
                api.register_event(EventType.on_collision, self.detect_collision)  # Register the freefall detection method
                
                if data:
                    match = re.match(r"X=(\d+), Y=(\d+), Button=(\d+)", data)
                    if match:
                        X, Y, Button = match.groups()
                        X = int(X)
                        Y = int(Y)
                        Button = int(Button)
                        stop_movement = True  # Initialize stop_movement
                        if Button == 0 and self.previous_button == 1:
                            self.toggle_calibration_mode(api, Y)  # Pass Y value to toggle_calibration_mode
                        self.previous_button = Button

                        current_time = time.time()

                        if current_time - self.last_heading_reset_time >= self.heading_reset_interval:
                            self.heading = 0
                            self.last_heading_reset_time = current_time

                        if self.calibration_mode:
                            self.enter_calibration_mode(api, Y)  # Call enter_calibration_mode with Y value
                        else:
                            # Use the calibrated base heading for movement
                            adjusted_heading = self.base_heading + self.heading
                            if X > 1000:
                                self.move(api, adjusted_heading, self.speed)  # Forward
                                stop_movement = False
                            elif X < 50:
                                self.move(api, adjusted_heading + 180, self.speed)  # Backward
                                stop_movement = False
                            if Y < 50:
                                self.move(api, adjusted_heading + 270, self.speed)  # Left
                                stop_movement = False
                            elif Y > 1000:
                                self.move(api, adjusted_heading + 90, self.speed)  # Right
                                stop_movement = False
                            if stop_movement:
                                api.set_speed(0)  # Stop

                        self.last_command_time = current_time
                else:
                    api.set_speed(0)
                    self.heading = 0
                    api.set_heading(self.heading)

            client_socket.close()

    # def detect_liftup(self, api):
    #         try:
    #             # Get the current acceleration data
    #             accel_data = api.get_acceleration()
                
    #             # Check if the acceleration in the z-axis is below a certain threshold
    #             threshold_z = 1.65  # Adjust this value based on your testing
    #             if accel_data['z'] > threshold_z:
    #                 print("Ball is being lifted up!")
                    
    #                 # Perform any additional actions, such as changing LED color
    #                 api.set_main_led(Color(0, 0, 255))  # Set LED to blue
                    
    #                 # Wait for a short duration before continuing
    #                 time.sleep(0.5)
                    
    #                 # Reset the LED color if desired
    #                 api.set_main_led(Color(0, 255, 0))  # Set LED back to green
                    
    #         except struct.error:
    #             print("Error detecting lift-up!")
    #         except ValueError:
    #             print("Error detecting lift-up!")
    #         except:
    #             print("Error detecting lift-up!")

    def detect_freefall(self, api):
        try:
            # Get the current acceleration data
            accel_data = api.get_acceleration()
            
            # Check if the acceleration magnitude is below a certain threshold
            if self.is_freefall(accel_data):
                # Freefall detected
                print("LIFT UP detected!")
                # Perform additional actions...

        except Exception as e:
            print(f"Error detecting freefall: {e}")
    def is_freefall(self, accel_data):
        # Calculate the acceleration magnitude
        accel_mag = (accel_data['z'] ** 2) 
        return accel_mag < self.threshold_accel_mag

    def print_battery_level(self, api):
        battery_voltage = Power.get_battery_voltage(self.toy)
        print(battery_voltage)

    def detect_collision(self, event):
        print("Collision detected!")
        print(self.collision_occurred)  # Event data
        self.collision_occurred = True  # Set collision occurred flag to True

    def detect_landing(self, event):
        print("LANDED!")


def main():
    sphero_obj = SpheroController()
    sphero_obj.discover_toy()
    if sphero_obj.toy:
        sphero_obj.control_toy()

if __name__ == "__main__":
    main()
