#ifndef _MODEL_H_
#define _MODEL_H_

#include <algorithm>
#include <array>
#include <cstdlib>
#include <functional>
#include <map>
#include <memory>
#include <mutex>
#include <string>
#include <time.h>
#include <vector>

#include <opencv2/opencv.hpp>

#include "globals.h"
#include "log.h"

/** @brief Recognition classes. */
namespace Recog {
    
    /** @brief Exception of Recog components. */
    class Exception: public std::exception {
        public:
            /**
             * @brief Constructor.
             * @param msg       Description of exception.
             */
            Exception(const char *msg): msg_(msg) {}
            /**
             * @brief Description getter.
             * @returns Description of exception.
             */
            std::string what() { return std::string(msg_); }
        private:
            const char * msg_; /**< Description */
    };


    /** @brief Recognized object in polar coordinates. */
    typedef Geo::Coords::Polar Object;

    /** @brief Features extracted from the signal. */
    typedef cv::Mat Features;
    
    /** @brief Result of recognition (objects) to send. */
    struct Result {
        unsigned timestamp; /**< Timestamp of object. */
        std::vector<Object> data; /**< Recognized objects. */

        /** @brief Formatted print. */
        void log() {
            std::cerr << "Result " << timestamp << ": ";
            for(auto &it: data) {
                it.log();
                std::cerr << " ";
            }
            if(data.size() > 0) std::cerr << "\x08.\n"; // bksp
            else std::cerr << "No objects detected.\n";
        }

        /**
         * @brief Buffer size getter.
         * @returns Buffer size in B.
         */
        unsigned bufferSize() { return (1 + data.size()*2) * sizeof(int); }

        /**
         * @brief Raw buffer exporter. Used when sending data.
         *        The data has following format:
         *          4B object count N, n*(4+4)B object data
         *          Object data contains azimuth and distance.
         *        Endianness not solved. 
         * @returns Buffer address in memory.
         */
        void * toBuffer() {
            // allocate, reallocate if allocated
            if(mem_ != nullptr) { delete[] mem_; }
            int* buffer = new int [ 1 + data.size()*2 ];
            // first 4 bytes is count of objects
            buffer[0] = data.size();
            // pairs of values (azimuth[4B]+distance[4B])  
            for(unsigned i = 0; i < data.size(); i++) {
                buffer[1 + 2*i] = data[i].azimuth;
                buffer[1 + 2*i + 1] = data[i].distance;
            }
            return buffer;
        }
        /** @brief Destructor. Deallocates the buffer. */
        ~Result() { if(mem_ != nullptr) { delete[] mem_; } }

        private:
            int * mem_ = nullptr; /**< Buffer address. */
    };
}

/** @brief Hardware abstraction classes. */
namespace HW {

    /** @brief */
    class Exception: public Recog::Exception {};

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
                azimuth_(orientation), position_(position), name_(name) {
                
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
            
            /**
             * @brief Actualizes data. Performs feature extraction.
             */
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
            int azimuth_;      /**< Azimuth of the sensor relatively to the global azimuth. */
            Geo::Coords::Polar position_; /**< Position of the sensor relatively to the center. */

            std::mutex featureLock; /**< Lock of features for simultaneous access. */
            Recog::Features features_; /**< Features. */

            std::string name_; /**< Name of the sensor (for logging). */
            /** @brief Prints out prompt of sensor. */
            void DebugPrompt() { std::cerr << "Sensor " << name_ << ": "; }
    };

}

namespace Recog {

    /** @brief Fusion performing class. */
    class Fusion {
        public:
            /** @brief Constructor. */
            Fusion() {
                const int OMEGA = 50;
                // central sensor
                sensors_.emplace( "C", std::make_shared<HW::Sensor>("C") );
                // left sensor
                sensors_.emplace("L", std::make_shared<HW::Sensor>(
                    "L", // name
                    50,  // orientation
                    Geo::Coords::Polar ( // position
                        90+((180-OMEGA)/2.), // azimuth
                        sqrt(2*25*25 - 2*25*25*cos(OMEGA/360.*M_PI)) // distance
                    )
                ));
                // right sensor
                sensors_.emplace("R", std::make_shared<HW::Sensor>(
                    "R", // name
                    -50, // orientation
                    Geo::Coords::Polar( // position
                        -90-((180-OMEGA)/2.), // azimuth
                        sqrt(2*25*25 - 2*25*25*cos(-OMEGA/360.*M_PI)) // distance
                    )
                ));
            }
            /**
             * @brief Getter of actualizer of certain sensor.
             *        Used by Comm, when data arrives.
             * @param sensorkey     Sensor specifying (L,R,C).
             * @retuns Function handeling new segment.
             */
            std::function<void(std::array<int,SEGMENT_SIZE>)> getActualizer(std::string sensorkey) {
                std::shared_ptr<HW::Sensor> s = sensors_.at(sensorkey);
                return [s](std::array<int,SEGMENT_SIZE> data){ s->actualizeData(data); };
            }

            /**
             * @brief Fusion algorithm.
             * @returns Result of the fusion.
             */
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
            std::map<std::string, std::shared_ptr<HW::Sensor>> sensors_; /**< Sensor map. */
    };
}


#endif // _MODEL_H_