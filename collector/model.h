#ifndef _MODEL_H_
#define _MODEL_H_

#include <algorithm>
#include <array>
#include <cstdlib>
#include <functional>
#include <map>
#include <mutex>
#include <string>
#include <time.h>
#include <vector>

#include "globals.h"
#include "log.h"

namespace Recog {
    class Exception {
        public:
            Exception(const char *msg) { msg_ = msg; }
            std::string what() { return std::string(msg_); }
        private:
            const char * msg_;
    };

    typedef Geo::Coords::Polar Object;
    struct Result {
        unsigned timestamp;
        std::vector<Object> data;

        void log() {
            std::cerr << "Result " << timestamp << ": ";
            for(auto &it: data) {
                it.log();
                std::cerr << " ";
            }
            if(data.size() > 0) std::cerr << "\x08.\n";
            else std::cerr << "No objects detected.\n";
        }

        unsigned bufferSize() { return (1 + data.size()*2) * sizeof(int); }

        void * toBuffer() {
            if(mem != nullptr) { delete[] mem; }
            int* buffer = new int [ 1 + data.size()*2 ];
            buffer[0] = data.size();
            for(unsigned i = 0; i < data.size(); i++) {
                buffer[1 + 2*i] = data[i].azimuth;
                buffer[1 + 2*i + 1] = data[i].distance;
            }
            return buffer;
        }

        ~Result() { if(mem != nullptr) { std::cerr << "Result::~Result: Deallocating buffer.\n"; delete[] mem; } }

        private:
            int * mem = nullptr;
    };

    struct Features {
        static const unsigned featN = 13;
        unsigned timestamp;
        std::array<int, featN> data;

        bool old() { return (data.size() == 0); }
    };
}

namespace HW {
    class Exception {
        public:
            Exception(const char *msg) { msg_ = msg; }
            std::string what() { return std::string(msg_); }
        private:
            const char * msg_;
    };

    /**
     * @brief Abstraction of sensor.
     */
    class Sensor {
        public:
            /**
             * @brief Constructor.
             * @param name          Name of the sensor.
             * @param orientation   Azimuth of orientation of the sensor.
             * @param position      Position of the sensor in polar coordinates.
             *                      Relative to the top center.
             */
            Sensor(std::string name = "",
                   int orientation = 0,
                   Geo::Coords::Polar position = Geo::Coords::Polar()):
                name_(name), azimuth_(orientation), position_(position) {
                
                #ifdef DEBUG_SENSOR
                    DebugPrompt(); std::cerr << "Created. "
                                             << "Orientation [" << azimuth_ << "]. "
                                             << "Position "; position_.log(); std::cerr << ".\n";
                #endif
            }

            /**
             * @brief Name getter.
             * @returns Name of the sensor.
             */
            std::string name() { return name_; }

            
            /**
             * @brief Reads last data from sensor.
             * @returns Feature vector.
             */
            Recog::Features readFeatures() {
                featureLock.lock();
                Recog::Features f;
                std::swap(f, features_);
                return (featureLock.unlock(), f);
            }
            
            void actualizeData(std::array<int, SEGMENT_SIZE> samples) {
                
                #ifdef DEBUG_SENSOR
                    DebugPrompt(); std::cerr << "Data actualized.\n";
                #endif
                Recog::Features newfeatures;

                /* Feature extraction */
                /* samples -> newfeatures */
                (void)samples;

                // publish the features
                featureLock.lock();
                std::swap(newfeatures, features_);
                featureLock.unlock();
            }


        private:
            std::string name_;
            int azimuth_;
            Geo::Coords::Polar position_;

            std::mutex featureLock;
            Recog::Features features_;

            static const unsigned featN_ = 13;

            void DebugPrompt() {
                std::cerr << "Sensor " << name_ << ": ";
            }
    };
}

namespace Recog {
    class Fusion {
        public:
            Fusion() {
                const int OMEGA = 50;
                // central sensor
                sensors_.emplace( "C", new HW::Sensor("C") );
                // left sensor
                sensors_.emplace("L", new HW::Sensor( "L", // name
                                                50,  // orientation
                                                Geo::Coords::Polar ( // position
                                                    90+((180-OMEGA)/2.), // azimuth
                                                    sqrt(2*25*25 - 2*25*25*cos(OMEGA/360.*M_PI)) // distance
                                                )
                ));
                // right sensor
                sensors_.emplace("R", new HW::Sensor( "R", // name
                                                -50, // orientation
                                                Geo::Coords::Polar( // position
                                                    -90-((180-OMEGA)/2.), // azimuth
                                                    sqrt(2*25*25 - 2*25*25*cos(-OMEGA/360.*M_PI)) // distance
                                                )
                ));
            }

            std::function<void(std::array<int,SEGMENT_SIZE>)> getActualizer(std::string sensorkey) {
                HW::Sensor* s = sensors_.at(sensorkey);
                return [s](std::array<int,SEGMENT_SIZE> data){ s->actualizeData(data); };
            }

            Result calculate() {
                // read features from sensors
                Features fc = sensors_.at("C")->readFeatures();
                Features fl = sensors_.at("L")->readFeatures();
                Features fr = sensors_.at("R")->readFeatures();

                Result r;
                /* Do calculations (Features -> Object). */
                /* Not refreshed features are empty. */

                return r;
            }

        private:
            std::map<std::string, HW::Sensor*> sensors_;
    };
}


#endif // _MODEL_H_