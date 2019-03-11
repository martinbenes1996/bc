#ifndef PIR_H
#define PIR_H

#ifdef ARDUINO
    #include <Arduino.h>
#endif


class PIR {
    public:
        /**
         * @brief Constructor.
         * @param pin       Pin with sensor connected.
         */
        PIR(int);
        
        /**
         * @brief Initializer.
         * @param fs        Sampling frequency.
         */
        void begin(double);


        /**
         * @brief Read instantaneous value.
         * @returns Value of signal.
         */
        int read();

        int T() { return 1000./_fs; }


    private:
        int _pin;
        double _fs = 1.;
        int _lastread = 0;

        long sinceLast() { return abs(_lastread - millis()); }
        bool readNow() { return sinceLast() > T(); }
        
};

class SampleBuffer {
    public:
        /**
         * @brief Constructor.
         * @param maxsize       Maximal size of buffer.
         */
        SampleBuffer(int maxsize = 8092);
        /**
         * @brief Destructor.
         */
        ~SampleBuffer();


        /**
         * @brief Initializer.
         * @param sensor        Reference to sensor to read from.
         * @param segment       Segment size.
         * @param overlap       Overlap size.
         */
        void begin(PIR*, int, int);
        /**
         * @brief Sample sensor to buffer. Call in loop() function.
         */
        void sample();
        /**
         * @brief Getter of buffer.
         * @returns The buffer.
         */
        uint8_t* get();


    private:
        int _maxsize;
        int* _buffer;

        int _segment;
        int _overlap;
        PIR *_sensor;
        int _it;
        bool _reinit;
};

//include "pir/pirdefinitions.h"

#endif // PIR_H