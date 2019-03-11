
/* ------ CONSTANTS ------ */
#define Fs 100
#define SEGMENT 60
#define OVERLAP 10
/* ----------------------- */

#include <Arduino.h>
#include "PIR.h"



sensor = PIR(A0);
buffer = SampleBuffer();

void setup() {
    sensor.begin(Fs);
    buffer.begin(&sensor, SEGMENT, OVERLAP);
}

void loop() {
    buffer.sample();
}


int main() {
    setup();
    while(true) { loop(); }
}



