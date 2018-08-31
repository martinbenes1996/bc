#define SMPL_AVG_CNT 100
int analogPin = 3;
int mem[SMPL_AVG_CNT];
int p = 0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  if(p < SMPL_AVG_CNT) {
    mem[p++] = analogRead(analogPin);
  }
  else {
    int n = SMPL_AVG_CNT;
    p = 0;
    long sum;
    for(int i = 0; i < n; i++) {
      sum += mem[i];
    }
    double avg = (double)sum / (double)n;
    Serial.println(avg);
  }
}
