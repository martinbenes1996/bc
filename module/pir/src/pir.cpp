

#include "pir.h"

PIR::PIR(int pin): _pin(pin) {}

void PIR::begin(double fs) { 
    _fs = fs;
    _lastread = millis();    
}

int PIR::read() {
    if(!readNow()) { delay( T() - sinceLast() ); }
    _lastread = millis();
    return analogRead(_pin);
}

SampleBuffer::SampleBuffer(int maxsize): _maxsize(maxsize) {
    _buffer = new int[_maxsize];
}

SampleBuffer::~SampleBuffer() {
    delete[] _buffer;
}

void SampleBuffer::begin(PIR* sensor, int segment, int overlap) {
    _sensor = sensor;
    _segment = segment;
    _overlap = overlap;
    _reinit = false;
    _it = 0;
    for(int i = 0; i < _overlap; i++) {
        sample();
    }
}

void SampleBuffer::sample() {
    if( _reinit ) {
        for(int i = 0; i < _overlap; i++) {
            _buffer[i] = _buffer[_segment-_overlap+i];
        }
        _it = _overlap;
        _reinit = false;
    }
    if( _it < _segment ) {
        _buffer[_it++] = _sensor->read();
    }
}

uint8_t* SampleBuffer::get() {
    for(int i = _it; i < _segment; i++) {
        sample();
    }
    _reinit = true;
    return (uint8_t*)_buffer;
}
