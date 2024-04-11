/**
This Arduino script controls a NeoPixel ring to simulate the activity of different brain zones. 
It implements a gradual transition between different colors for the parietal, frontal, and temporal zones of the brain, creating a smooth and visually engaging representation of brain activity. 
The script defines functions to set pixels with gradual color transitions, allowing for customizable and dynamic lighting patterns reflecting the simulated brain activity.

**/


#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
 #include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif

int pariental[2] = {0, 7};
int temporalLeft[2] = {8, 15};
int temporalRight[2] = {16, 23};
int temporal[2] = {8, 23};
int frontal[2] = {24, 31};

// Which pin on the Arduino is connected to the NeoPixels?
#define PIN        D6 // On Trinket or Gemma, suggest changing this to 1

// How many NeoPixels are attached to the Arduino?
#define NUMPIXELS 32 // Popular NeoPixel ring size

// When setting up the NeoPixel library, we tell it how many pixels,
// and which pin to use to send signals. Note that for older NeoPixel
// strips you might need to change the third parameter -- see the
// strandtest example for more information on possible values.
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

#define DELAYVAL 500 // Time (in milliseconds) to pause between pixels

void setup() {
  // These lines are specifically to support the Adafruit Trinket 5V 16 MHz.
  // Any other board, you can remove this part (but no harm leaving it):
#if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)
  clock_prescale_set(clock_div_1);
#endif
  // END of Trinket-specific code.

  pixels.begin(); // INITIALIZE NeoPixel strip object (REQUIRED)
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
  setPixelsFade(frontal, pixels.Color(0, 0, 255), pixels.Color(0, 0, 50), DELAYVAL);
  delay(1000);
  setPixelsFade(temporal, pixels.Color(0, 255, 0), pixels.Color(0, 50, 0), DELAYVAL);
  delay(1000);
  setPixelsFade(pariental, pixels.Color(255, 0, 0), pixels.Color(50, 0, 0), DELAYVAL);
  delay(1000);
}
