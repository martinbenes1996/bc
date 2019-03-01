
/* -------- PARAMETERS --------- */
#define SEGMENT 60                /* segment size */
#define OVERLAP 10                /* overlap size */
#define SAMPLE_FREQUENCY 100      /* sampling frequency */
#define SEND_FREQUENCY 2          /* sending frequency  */
/* ---------------------------- */





// derived parameters
#define SAMPLE_PERIOD (1000/SAMPLE_FREQUENCY)
#define SEND_PERIOD (1000/SEND_FREQUENCY)

// globals
int lastRead;
int lastSend;
int mem[SEGMENT];
int memIt = 0;

// SETUP
void setup() {
  analogReference(DEFAULT);
  Serial.begin(9600);        // initialize serial

  // preread overlap
  for(int i = 0; i < OVERLAP; i++) {
    readSample();
    delay(SAMPLE_PERIOD);
  }
  lastSend = lastRead = millis();
  memIt = OVERLAP;
}

// LOOP
void loop(){
  // read
  int now = millis();
  if( abs(now-lastRead) > SAMPLE_PERIOD ) {
    readSample();
  }
  // send
  now = millis();
  if( abs(now-lastSend) > SEND_PERIOD ) {
    sendSegment();
    lastSend = millis();
  }
}

// READ SAMPLE
void readSample() {
  if(memIt >= SEGMENT) return;
  mem[memIt++] = analogRead(A0);
  lastRead = millis();
}

// SEND SEGMENT
void sendSegment() {
  // read missing
  for(int i = memIt; i < SEGMENT; i++) {
    readSample();
    delay(SAMPLE_PERIOD);
  }
  // send
  for(int i = 0; i < memIt; i++) {
    Serial.println(mem[i]);
  }
  // move overlap
  memcpy(mem, &mem[SEGMENT - OVERLAP], OVERLAP*sizeof(int));
  memIt = OVERLAP;
}



