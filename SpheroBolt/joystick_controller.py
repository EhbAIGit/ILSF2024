# arduino.py

import socket
import serial
import re

# Open the serial port
ser = serial.Serial('COM3', 9600)

# Create a server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 5555))
server_socket.listen(1)

while True:
    # Accept incoming connection
    client_socket, client_address = server_socket.accept()
    
    while True:
        # Read a line (ending with \n) from the serial port
        line = ser.readline().decode('utf-8').strip()
        
        # Use regular expressions to extract the values
        match = re.match(r"X=(\d+), Y=(\d+), Button=(\d+)", line)
        
        if match:
            X, Y, Button = match.groups()
            X = int(X)
            Y = int(Y)
            Button = int(Button)
            data = f"X={X}, Y={Y}, Button={Button}"
            print(data)
            # Send data to the connected client (sphero_controller.py)
            client_socket.send(data.encode('utf-8'))
        else:
            print("No matching data found.")

    client_socket.close()
