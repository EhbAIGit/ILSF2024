/**
This code controls a NeoPixel strip to simulate the activity of different brain zones. 
It listens for serial commands ('f' for frontal, 't' for temporal, 'p' for parietal) and changes the color of the corresponding LED zone gradually, 
creating a smooth transition effect. 
The loop continuously checks for incoming serial commands and executes the corresponding action based on the received command.
**/




#include <Adafruit_NeoPixel.h>

// Define the pins for the NeoPixels
#define PIN        D6
#define NUMPIXELS 32

// Define the colors for each brain zone
#define FRONTAL_COLOR pixels.Color(0, 0, 255)
#define TEMPORAL_COLOR pixels.Color(0, 255, 0)
#define PARIETAL_COLOR pixels.Color(255, 0, 0)

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

// Define the pixel ranges for each brain zone
int frontal[2] = {24, 31};
int temporal[2] = {8, 23};
int parietal[2] = {0, 7};

void setup() {
  pixels.begin();
  Serial.begin(9600); // Initialize serial communication
}

void setPixelsFade(int pixelPos[2], uint32_t startColor, uint32_t endColor, int transitionTime) {
  int steps = 50;
  int wait = transitionTime / steps;

  for (int i = 0; i <= steps; i++) {
    int r = map(i, 0, steps, (startColor >> 16) & 0xFF, (endColor >> 16) & 0xFF);
    int g = map(i, 0, steps, (startColor >> 8) & 0xFF, (endColor >> 8) & 0xFF);
    int b = map(i, 0, steps, startColor & 0xFF, endColor & 0xFF);

    uint32_t newColor = pixels.Color(r, g, b);

    for (int j = pixelPos[0]; j <= pixelPos[1]; j++) {
      pixels.setPixelColor(j, newColor);
    }

    pixels.show();
    delay(wait);
  }
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    switch (command) {
      case 'f': // Frontal zone
        setPixelsFade(frontal, pixels.Color(0, 0, 255), pixels.Color(0, 0, 50), 50);
        break;
      case 't': // Temporal zone
        setPixelsFade(temporal, pixels.Color(0, 255, 0), pixels.Color(0, 50, 0), 50);
        break;
      case 'p': // Parietal zone
        setPixelsFade(parietal, pixels.Color(255, 0, 0), pixels.Color(50, 0, 0), 50);
        break;
      default:
        // Invalid command
        break;
    }
  }
}
