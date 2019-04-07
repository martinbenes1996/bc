

/* -------- PARAMETERS --------- */
#define SEGMENT 220                 /* segment size */
#define OVERLAP 20                  /* overlap size */
#define SAMPLE_FREQUENCY 100        /* sampling frequency */
#define SEND_FREQUENCY 0.5          /* sending frequency  */
/* ---------------------------- */


// parameters
int sampleFrequency = SAMPLE_FREQUENCY;
int sendFrequency = SEND_FREQUENCY;
int samplePeriod = (1000 / SAMPLE_FREQUENCY);
int sendPeriod = (1000 / SEND_FREQUENCY);

// globals
int lastRead = 0;
int lastSend = 0;
int mem[SEGMENT];
int memIt = 0;

void setup() {
  Serial.begin(9600);
  delay(10);

  // WiFi_reset();
  
  pinMode(LED_BUILTIN, OUTPUT); digitalWrite(LED_BUILTIN, HIGH);
  pinMode(2, OUTPUT); digitalWrite(2, HIGH);

  // preread overlap
  for(int i = 0; i < OVERLAP; i++) { readSample(); delay(samplePeriod); }
  lastSend = lastRead = millis();
  memIt = OVERLAP;
}

void loop() {
  int now = millis();

  // read
  now = millis();
  if(abs(now-lastRead) > samplePeriod) { readSample(); }
  // send
  now = millis();
  if(abs(now-lastSend) > sendPeriod) { sendSegment(); }
  // not connected
  
}


void readSample() {
  if(memIt < SEGMENT) { mem[memIt++]=analogRead(A0); lastRead=millis(); }
}

void sendSegment() {
  digitalWrite(LED_BUILTIN, LOW); // led on

  // read missing
  for(int i = memIt; i < SEGMENT; i++) { readSample(); delay(samplePeriod); }
  // send
  for(int i = 0; i < memIt; i++) { Serial.println(mem[i]); }
  // move overlap
  memcpy(mem, &mem[SEGMENT-OVERLAP], OVERLAP*sizeof(int));
  memIt = OVERLAP;
  lastSend=millis();
  
  digitalWrite(LED_BUILTIN, HIGH); // led off
}
