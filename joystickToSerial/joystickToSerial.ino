void setup() {
  // Initialiseer de seriële communicatie
  Serial.begin(9600);

  // Configureer de pinmodi
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(9, INPUT); // Configureer GPIO 8 als input voor de knop
  pinMode(9, INPUT_PULLUP);
  // Er is geen noodzaak om de random seed te initialiseren aangezien we werkelijke waarden lezen
}

void loop() {
  // Lees de werkelijke waarden van de analoge inputs
  int x = analogRead(A0); // Leest de waarde van A0 (0 tot 1023)
  int y = analogRead(A1); // Leest de waarde van A2 (0 tot 1023)

  // Lees de status van de knop (HIGH of LOW)
  int buttonState = digitalRead(9); // Leest de digitale status van pin 8

  // Druk de gelezen waarden af naar de seriële monitor
  Serial.print("X=");
  Serial.print(x);
  Serial.print(", Y=");
  Serial.print(y);
  Serial.print(", Button=");
  Serial.println(buttonState);


  // Voeg hier een korte vertraging toe om de bemonsteringsfrequentie te beheersen
  delay(100); // Wacht een beetje voordat je de loop herhaalt, indien nodig
}
