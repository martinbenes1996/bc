

#include "led.h"

LED::LED(int pin): _pin(pin) {
	_t = millis();
	_mode = Mode::Off;
	on();
}


void LED::setMode(Mode mode, long T_on, long T_off) {
	_mode = mode;	
	_T_on = T_on;
	_T_off = T_off;
	_mode_en = true;
}

void LED::indicate() {
	if(!_mode_en) { return; }
	if((millis()-_t) < _T_on) {
		digitalWrite(_pin, LOW);			
	} else if((millis()-_t) < (_T_on+_T_off)) {
		digitalWrite(_pin, HIGH);
	} else {
		_t = millis();
	}
}

void LED::on() {
	_mode_en = false;
	digitalWrite(_pin, LOW);
}
void LED::off() {
	_mode_en = false;
	digitalWrite(_pin, HIGH);
}

