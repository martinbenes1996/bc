
/* -------- PARAMETERS --------- */
#define SEGMENT 220                 /* segment size */
#define OVERLAP 20                  /* overlap size */
#define SAMPLE_FREQUENCY 100        /* sampling frequency */
#define SEND_FREQUENCY 0.5          /* sending frequency  */

//const char * WiFi_ssid = "Serepetička";
//const char * WiFi_password = "17222813";
const char * WiFi_ssid = "KOLPING1";
const char * WiFi_password = "XZ8T7UK5KAs";
/* ---------------------------- */


#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <WiFiUDP.h>

// parameters
int sampleFrequency = SAMPLE_FREQUENCY;
int sendFrequency = SEND_FREQUENCY;
int samplePeriod = (1000 / sampleFrequency);
int sendPeriod = (1000 / sendFrequency);

// renewers
void renewSamplePeriod() {
  samplePeriod = (1000 / sampleFrequency);
}
void renewSendPeriod() {
  sendPeriod = (1000 / sendFrequency);
}
// setters
void setSampleFrequency(int val) {
  sampleFrequency = val;
  renewSamplePeriod();
}
void setSendFrequency(int val) {
  sendFrequency = val;
  renewSendPeriod();
}
void setSamplePeriod(int val) {
  setSampleFrequency(1000 / val);
}
void setSendPeriod(int val) {
  setSendFrequency(1000 / val);
}

// globals
int lastRead;
int lastSend;
int mem[SEGMENT];
int memIt = 0;

// comm
ESP8266WebServer server(80);
WiFiUDP udp;
bool ucastEn = false, mcastEn = true, bcastEn = false;
IPAddress ucastAddress(10, 0, 0, 1);
IPAddress mcastAddress(224, 0, 0, 1);
uint16_t ucastPort = 1234, mcastPort = 1234, bcastPort = 1234;


// SETUP
void setup() {
  //analogReference(DEFAULT);
  Serial.begin(9600);        // initialize serial
  pinMode(LED_BUILTIN, OUTPUT);

  WiFi_Init();
  HTTP_Init();

  // preread overlap
  for (int i = 0; i < OVERLAP; i++) {
    readSample();
    delay(samplePeriod);
  }
  lastSend = lastRead = millis();
  memIt = OVERLAP;
}

// LOOP
void loop() {
  server.handleClient();

  // read
  int now = millis();
  if ( abs(now - lastRead) > samplePeriod ) {
    readSample();
  }
  // send
  now = millis();
  if ( abs(now - lastSend) > sendPeriod ) {
    sendSegment();
    lastSend = millis();
  }
}

// READ SAMPLE
void readSample() {
  if (memIt >= SEGMENT) return;
  mem[memIt++] = analogRead(A0);
  lastRead = millis();
}

// SEND SEGMENT
void sendSegment() {
  // led on
  digitalWrite(LED_BUILTIN, LOW);
  // read missing
  for (int i = memIt; i < SEGMENT; i++) {
    readSample();
    delay(samplePeriod);
  }
  // send
  // network
  if (mcastEn) {
    sendMCast();
  }
  if (ucastEn) {
    sendUCast();
  }
  if (bcastEn) {
    sendBCast();
  }
  // serial
  for (int i = 0; i < memIt; i++) {
    Serial.println(mem[i]);
  }
  // move overlap
  memcpy(mem, &mem[SEGMENT - OVERLAP], OVERLAP * sizeof(int));
  memIt = OVERLAP;
  // led off
  digitalWrite(LED_BUILTIN, HIGH);
}

void sendMCast() {
  udp.beginPacketMulticast(mcastAddress, mcastPort, WiFi.localIP());
  udp.write((const uint8_t*)mem, SEGMENT * sizeof(int));
  udp.endPacket();
}

void sendUCast() {
  udp.beginPacket(ucastAddress, ucastPort);
  udp.write((const uint8_t*)mem, SEGMENT * sizeof(int));
  udp.endPacket();
}
void sendBCast() {
  // send by broadcast
}

void WiFi_Init() {
  WiFi.begin(WiFi_ssid, WiFi_password);             // Connect to the network
  Serial.print(WiFi_ssid); Serial.println(": Connecting...");

  int i = 0;
  while (WiFi.status() != WL_CONNECTED) { // Wait for the Wi-Fi to connect
    delay(1000);
    Serial.print(++i); Serial.print(' ');
  }

  Serial.println('\n');
  Serial.println("Connection established!");
  Serial.print("IP address:\t");
  Serial.println(WiFi.localIP());         // Send the IP address of the ESP8266 to the computer
}

void HTTP_Init() {
  server.on("/config/ucast", handleUCast);
  server.on("/config/mcast", handleMCast);
  server.on("/config/bcast", handleBCast);
  server.on("/config/sample", handleSample);
  server.on("/config/send", handleSend);
  server.onNotFound([]() {
    server.send(404, "text/plain", "404: Not found");
  });
  server.begin();
}

void handleUCast() {
  // enabled
  if (server.arg("enabled") == "true") {
    ucastEn = true;
  }
  if (server.arg("enabled") == "false") {
    ucastEn = false;
  }
  // address
  if (server.arg("address") != "") {
    IPAddress addr;
    if (addr.fromString(server.arg("address"))) {
      ucastAddress = addr;
    }
  }
  // port
  if (server.arg("port") != "") {
    ucastPort = server.arg("port").toInt();
  }
  // send response
  String response = "Unicast Settings:\n===================\nEnabled: ";
  response += ((ucastEn) ? 1 : 0);
  response += "\nAddress: ";
  response += ucastAddress.toString();
  response += "\nPort: ";
  response += ucastPort;
  response += "\n";
  server.send(200, "text/plain", response);
}

void handleMCast() {

  // enabled
  if (server.arg("enabled") == "true") {
    mcastEn = true;
  }
  if (server.arg("enabled") == "false") {
    mcastEn = false;
  }
  // address
  if (server.arg("address") != "") {
    IPAddress addr;
    if (addr.fromString(server.arg("address"))) {
      mcastAddress = addr;
    }
  }
  // port
  if (server.arg("port") != "") {
    mcastPort = server.arg("port").toInt();
  }
  // send response
  String response = "Multicast Settings:\n===================\nEnabled: ";
  response += ((mcastEn) ? 1 : 0);
  response += "\nAddress: ";
  response += mcastAddress.toString();
  response += "\nPort: ";
  response += mcastPort;
  response += "\n";
  server.send(200, "text/plain", response);
}

void handleBCast() {
  // enabled
  if (server.arg("enabled") == "true") {
    bcastEn = true;
  }
  if (server.arg("enabled") == "false") {
    bcastEn = false;
  }
  // port
  if (server.arg("port") != "") {
    bcastPort = server.arg("port").toInt();
  }
  // send response
  String response = "Broadcast Settings:\n===================\nEnabled: ";
  response += ((bcastEn) ? 1 : 0);
  response += "\nPort: ";
  response += bcastPort;
  response += "\n";
  server.send(200, "text/plain", response);
}

void handleSample() {
  bool fwas = false;
  int f = -1, T = -1;
  // frequency
  if (server.arg("frequency") != "") {
    f = server.arg("frequency").toInt();
    fwas = true;
  }
  // period
  if (server.arg("period") != "") {
    if (fwas) {
      server.send(400, "text/plain", "400: Bad request");
      return;
    }
    T = server.arg("period").toInt();
  }
  if (f != -1) {
    setSampleFrequency(f);
  }
  else if (T != -1) {
    setSamplePeriod(T);
  }

  // send response
  String response = "Sample Settings:\n===================\nFrequency: ";
  response += sampleFrequency;
  response += "\nPeriod: ";
  response += samplePeriod;
  response += "\n";
  server.send(200, "text/plain", response);
}

void handleSend() {
  bool fwas = false;
  int f = -1, T = -1;
  // frequency
  if (server.arg("frequency") != "") {
    f = server.arg("frequency").toInt();
    fwas = true;
  }
  // period
  if (server.arg("period") != "") {
    if (fwas) {
      server.send(400, "text/plain", "400: Bad request");
      return;
    }
    f = server.arg("period").toInt();
  }
  if (f != -1) {
    setSendFrequency(f);
  }
  else if (T != -1) {
    setSendPeriod(T);
  }

  // send response
  String response = "Send Settings:\n===================\nFrequency: ";
  response += sendFrequency;
  response += "\nPeriod: ";
  response += sendPeriod;
  response += "\n";
  server.send(200, "text/plain", response);
}




