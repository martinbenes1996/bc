#ifndef LED_H
#define LED_H

#ifdef ARDUINO
    #include <Arduino.h>
#endif


class LED {
	public:
		/**
		 * @brief Mode of the LED.
		 */
		enum Mode {
			On, 	/**< Light on. */
			Blink,  /**< Blink. */
			Off,	/**< Light off. */
		};

		/**
		 * @brief Constructor.
		 * @param pin		Pin number.
		 */
		LED(int);

		/**
		 * @brief Mode setter.
		 * @param mode 		New mode to set.
		 * @param T_on		Time on.
		 * @param T_off		Time off.
		 */
		void setMode(Mode mode, long T_on = 500, long T_off = 500);
		/**
		 * @brief Process. Called in loop().
		 */
		void indicate();

		void on();
		void off();

	private:
		int _pin;
		bool _mode_en;
		Mode _mode; /**< Mode of LED. */
		long _T_on; /**< Time of being turned on. */
		long _T_off; /**< Time of being turned off. */
		long _t; /**< Last iteration begin. */
};

#endif // LED_H
