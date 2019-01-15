/*  
    Arduino with PIR motion sensor
    For complete project details, visit: http://RandomNerdTutorials.com/pirsensor
    Modified by Rui Santos based on PIR sensor by Limor Fried
*/
 
//int led = 13;                // the pin that the LED is atteched to
//int sensor = 2;             // sensor 1
//int Ch1 = A0;
//int Ch2 = A1;
//int cnt = 0;

void setup() {
  analogReference(DEFAULT);
  //pinMode(led, OUTPUT);      // initalize LED as an output
  //pinMode(sensor, INPUT);   // initialize sensor as an input
  Serial.begin(9600);        // initialize serial
}

void loop(){
  //int val = digitalRead(sensor);
  // DISCRETE
  //if(val == HIGH) {
    //Serial.print("Motion Detected: ");
    //Serial.println(++cnt);
    //digitalWrite(led, HIGH);
    //delay(200);
    //digitalWrite(led, LOW);
  //}
  // continuous
  /*
  int val1 = analogRead(Ch1);
  int val2 = analogRead(Ch2);
  float v1 = val1*5.0 / 1023;
  float v2 = val2*5.0 / 1023;

  if(val == LOW) {
    
  } else {
    Serial.print(v1);
    Serial.print(" ");
    Serial.println(v2);
    delay(100);
 }*/

 //analogWrite(A7, 255);
 int val = analogRead(A0);
 Serial.println(val);
 delay(10);
}
