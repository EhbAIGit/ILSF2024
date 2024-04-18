import cv2
import numpy as np
from collections import Counter

def get_dominant_color(frame):
    # Convert from BGR to RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Reshape the frame to be a list of pixels
    pixels = frame.reshape((-1, 3))

    # Count the frequency of each color
    most_common = Counter(map(tuple, pixels)).most_common(1)

    return most_common[0][0]

# Start capturing from the first camera source
cap = cv2.VideoCapture(0)

try:
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            break

        # Get the dominant color
        dominant_color = get_dominant_color(frame)
        print("Dominant color (RGB):", dominant_color)

        # Display the resulting frame
        cv2.imshow('Frame', frame)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
