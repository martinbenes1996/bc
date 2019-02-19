
int lastRead;
int lastSend;
int mem[60];
int memIt = 0;

void setup() {
  analogReference(DEFAULT);
  Serial.begin(9600);        // initialize serial

  for(int i = 0; i < 10; i++) {
    readSample();
    delay(10);
  }
  lastSend = lastRead = millis();
  memIt = 10;
}

void loop(){
  int now = millis();
  if( abs(now-lastRead) > 10 ) {
    readSample();
  }

  now = millis();
  if( abs(now-lastSend) > 500 ) {
    sendSegment();
    lastSend = millis();
  }
  
}

void readSample() {
  if(memIt >= 60) return;
  mem[memIt++] = analogRead(A0);
  lastRead = millis();
}

void sendSegment() {
  for(int i = memIt; i < 60; i++) {
    readSample();
    delay(10);
  }
  for(int i = 0; i < memIt; i++) {
    Serial.println(mem[i]);
  }

  memcpy(mem, &mem[50], 10*sizeof(int));
  memIt = 10;
}



