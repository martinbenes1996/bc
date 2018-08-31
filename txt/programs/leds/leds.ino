// ESP8266 blikání dvou LED diod

// nastavení propojovacího pinu LED diody
#define LEDka 14

void setup() {
  // nastavení obou LED diod jako výstupních
  pinMode(LED_BUILTIN, OUTPUT);
  //pinMode(LEDka, OUTPUT);
}

void loop() {
  // blikání vestavěnou diodou na ESP,
  // pro zapnutí musíme přivést logickou 0 - LOW
  //digitalWrite(LED_BUILTIN, LOW);
  //delay(500);
  digitalWrite(LED_BUILTIN, HIGH);
  delay(1000);
  digitalWrite(LED_BUILTIN, LOW);
  delay(1000);
  //delay(1000);
  // blikání LED diodou na desce,
  // pro zapnutí musíme přivést logickou 1 - HIGH
  //digitalWrite(LEDka, HIGH);
  //delay(1000);
  //digitalWrite(LEDka, LOW);
  //delay(500);
}
