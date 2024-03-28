import serial
import re

# Open de seriële poort
ser = serial.Serial('COM7', 9600)

while True:
    # Lees een regel (eindigend op \n) van de seriële poort
    line = ser.readline().decode('utf-8').strip()
    # Gebruik reguliere expressies om de waarden te extraheren
    match = re.match(r"X=(\d+), Y=(\d+), Button=(\d+)", line)
    if match:
        X, Y, Button = match.groups()
        X = int(X)
        Y = int(Y)
        Button = int(Button)
        print(f"X={X}, Y={Y}, Button={Button}")
    else:
        print("Geen overeenkomende data gevonden.")
