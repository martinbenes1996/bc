// ESP8266 WiFi skener

// připojení potřebné knihovny
#include "ESP8266WiFi.h"

void setup() {
  // zahájení komunikace po sériové lince
  Serial.begin(9600);
  // nastavení WiFi do módu stanice a odpojení od předchozí sítě
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
}

void loop() {
  Serial.println("Zahajeni skenovani..");
  // načtení WiFi sítí v okolí a uložení jejich počtu do proměnné
  int n = WiFi.scanNetworks();
  // v případě nulového počtu sítí vypíšeme informaci
  // po sériové lince
  if (n == 0) {
    Serial.println("Zadne viditelne WiFi site v okoli.");
  }
  // pokud byly nalezeny WiFi sítě v okolí,
  // vypíšeme jejich počet a další informace
  else  {
    Serial.print(n);
    Serial.println(" WiFi siti v okoli. Seznam:");
    // výpis všech WiFi sítí v okolí,
    // vypíšeme název, sílu signálu a způsob zabezpečení
    for (int i = 0; i < n; ++i)
    {
      Serial.print(i + 1);
      Serial.print(": ");
      Serial.print(WiFi.SSID(i));
      Serial.print(" (");
      Serial.print(WiFi.RSSI(i));
      Serial.print(")");
      Serial.println((WiFi.encryptionType(i) == ENC_TYPE_NONE)?" ":"*");
      delay(10);
    }
  }
  // ukončení výpisu
  Serial.println("");
  // pauza po dobu pěti vteřin před novým skenováním
  delay(5000);
}
