#ifndef _MODEL_H_
#define _MODEL_H_

#include <cmath>
#include <cstdlib>
#include <time.h>

#include <algorithm>
#include <array>
#include <chrono>
#include <functional>
#include <map>
#include <memory>
#include <mutex>
#include <string>
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
            Exception(std::string msg): msg_(msg.c_str()) {}
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

    typedef std::function<float(long)> MotherWavelet;
    typedef std::function<MotherWavelet(unsigned)> Generator;
    /** @brief Representation of wavelet. */
    class Wavelet {
        // static methods
        public:
            static MotherWavelet Haar(unsigned s) {
                return [s](long x)->float {
                    if(x < 0) { return 0.; }
                    else if(x < (s/2.)) { return 1.; }
                    else if(x < (s)) { return -1.; }
                    else { return 0.; }
                };
            }
            static MotherWavelet Morlet(unsigned s) {
                return [s](long x)->float {
                    return exp(-(x*x)/2.) * cos(5.*x);
                };
            }
            static MotherWavelet MexicanHat(unsigned s) {
                return [s](long x)->float {
                    return pow(2., 5./4.) / sqrt(3.) * (1. + exp(2.*M_PI*x*x)) * exp(-M_PI*x*x);
                };
            }
        // instantional methods
        public:
            /**
             * @brief Wavelet constructor.
             * @param fGenerator        Generator of wavelet function with given scale (generator parameter).
             */
            Wavelet(Generator fGenerator): fGenerator_(fGenerator) {
                generateWavelet();
            }

            /**
             * @brief Convolution operator.
             * @param x         Input signal.
             * @returns Convolution with x.
             */
            float operator*(const cv::Mat& x);

            void setScale(unsigned s) {
                s_ = s;
                generateWavelet();
            }

            void setShift(long n) { shift_ = n; }

        private:
            Generator fGenerator_;
            void generateWavelet() { f_ = fGenerator_(s_); }

            MotherWavelet f_; /**< Wavelet core function. */
            unsigned s_ = 1;
            long shift_ = 0;
    };

    /** @brief Features extracted from the signal. */
    class Features {
        public:
            Features(cv::Mat x, Recog::Wavelet w) { extract(x,w); }
            Features(bool valid = false): valid_(valid) {}

            /**
             * @brief Performs CWF as feature extraction over input.
             * @param x         Input for CWF.
             * @param w         Used wavelet for transformation.
             * @returns CWF matrix (time x frequency).
             */
            void extract(cv::Mat x, Recog::Wavelet w);

            Features& operator=(const Features& o) {
                auto p = o.copyData();
                features_ = p.first;
                extracted_ = p.second;
                return *this;
            }
            std::pair<cv::Mat,bool> copyData() const { return std::make_pair(features_, extracted_); }

            cv::Mat get() {
                if(!extracted_) { throw Exception("Features::get: features not extracted yet"); }
                return features_;
            }

            bool valid() { return valid_; }

            int rows() { return features_.rows; }
            int cols() { return features_.cols; }

        private:
            const std::vector<unsigned> scales_ = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70}; /**< Scales for CWF. */

            cv::Mat features_;
            bool extracted_ = false;
            bool valid_ = false;
    };
    
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
                    DebugPrompt(); std::cerr << "Sensor(): Created. "
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
                Recog::Features f;

                featureLock.lock();
                    #ifdef DEBUG_FEATURES
                        DebugPrompt(); std::cerr << "readFeatures(): Features " << ((featuresValid())?"":"in") << "valid.\n";
                    #endif
                    if(featuresValid()) {
                        f = features_;
                    }
                featureLock.unlock();

                return f;
            }
            
            /**
             * @brief Actualizes data. Performs feature extraction.
             */
            void actualizeData(std::array<int, SEGMENT_SIZE> samples) {
                
                #ifdef DEBUG_SENSOR
                    DebugPrompt(); std::cerr << "actualizeData(): data actualized.\n";
                #endif

                // feature extraction
                cv::Mat x(1, SEGMENT_SIZE, CV_32S, samples.data());
                Recog::Wavelet w(Recog::Wavelet::MexicanHat); 
                Recog::Features newfeatures(x, w);

                // publish the features
                featureLock.lock();
                    features_ = newfeatures;
                    endFeatureUpdate();
                featureLock.unlock();
            }

        private:
            int azimuth_;      /**< Azimuth of the sensor relatively to the global azimuth. */
            Geo::Coords::Polar position_; /**< Position of the sensor relatively to the center. */

            std::mutex featureLock; /**< Lock of features for simultaneous access. */
            Recog::Features features_; /**< Features. */

            std::chrono::milliseconds lastUpdate;
            bool notUpdatedYet_ = true;
            bool featuresValid() {
                using namespace std::chrono;
                milliseconds now = duration_cast< milliseconds >( system_clock::now().time_since_epoch() );
                if(notUpdatedYet_) { return false; }
                if( duration_cast< milliseconds >(now-lastUpdate).count() > 500 ) { return false; }
                return true;
            }
            void endFeatureUpdate() {
                using namespace std::chrono;
                lastUpdate = duration_cast< milliseconds >( system_clock::now().time_since_epoch() );
                notUpdatedYet_ = false;
            }

            std::string name_; /**< Name of the sensor (for logging). */
            /** @brief Prints out prompt of sensor. */
            void DebugPrompt() { std::cerr << "HW::Sensor[" << name_ << "]::"; }
    };

}

namespace Recog {

    /** @brief Fusion performing class. */
    class Fusion {
        public:
            /** @brief Constructor. */
            Fusion();

            /**
             * @brief Getter of actualizer of certain sensor.
             *        Used by Comm, when data arrives.
             * @param sensorkey     Sensor specifying (L,R,C).
             * @retuns Function handeling new segment.
             */
            std::function<void(std::array<int,SEGMENT_SIZE>)> getActualizer(std::string);

            /**
             * @brief Fusion algorithm.
             * @returns Result of the fusion.
             */
            Result calculate();

        private:
            std::map<std::string, std::shared_ptr<HW::Sensor>> sensors_; /**< Sensor map. */
    };
}

namespace Fuzzy {

    /** @brief */
    class Exception: public Recog::Exception {
        public:
            Exception(const char* msg): Recog::Exception(msg) {}
            Exception(std::string msg): Recog::Exception(msg) {}
    };

    struct Index {
        Index(int r, int c): row(r), col(c) {}
        int row; /**< Row index. */
        int col; /**< Column index. */

    };

    class Matrix {
        public:
            Matrix(Recog::Features f): rowCount(f.rows()), colCount(f.cols()) {}
    
            double distance(Index i1, Index i2) {
                if(isInside(i1) && isInside(i2)) {
                    Geo::Coords::Polar i1p = toPolar(i1);
                    Geo::Coords::Polar i2p = toPolar(i2);

                    return pow(i1p.distance, 2) + pow(i2p.distance, 2) - 2*i1p.distance*i2p.distance*cos( abs(i1p.azimuth - i2p.azimuth) ); 
                } else { throw Exception("Fuzzy::Matrix::distance(): index out of range!"); }
            }

        private:
            const int rowCount;
            const int colCount;
            bool isInside(Index i) {
                return (i.row >= 0) && (i.row < rowCount) && (i.col >= 0) && (i.col < colCount);
            }

            const int rowCoef = 10; /**< Coefficient to calculate distance from row index. */
            const int colCoef = 10; /**< Coefficient to calculate azimuth from col index. */
            Geo::Coords::Polar toPolar(Index i) {
                Geo::Coords::Polar c;
                c.distance = i.row * rowCoef;
                c.azimuth = i.col * colCoef;
                return c;
            }

    };

}


#endif // _MODEL_H_