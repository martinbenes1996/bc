#ifndef _GLOBALS_H_
#define _GLOBALS_H_

#include <cmath>
#include <iostream>

namespace Geo {
    namespace Coords {

        /**
         * @brief Cartesian coordinates.
         */
        struct Cartesian {
            double x = 0;  /**< X coordinate. */
            double y = 0;  /**< Y coordinate. */
        };

        /**
         * @brief Polar coordinates.
         */
        struct Polar {
            Polar(int a = 0, int d = 0): azimuth(a), distance(d) {}
            int azimuth = 0;    /**< Azimuth of the point. */
            int distance = 0;   /**< Distance of the point. */

            /**
             * @brief Polar to Cartesian convertor.
             * @param scale     Scale of distance.
             * @returns Cartesian coordinates.
             */
            struct Cartesian toCartesian(int scale) {
                struct Cartesian c;
                c.x = cos(azimuth/360. * 2*M_PI)*distance*scale;
                c.y = sin(azimuth/360. * 2*M_PI)*distance*scale;
                return c;
            }

            void log() {
                std::cerr << "[A " << azimuth << ", D " << distance << "]"; 
            }
        };

    }
}

#define SEGMENT_SIZE 240

#endif // _GLOBALS_H_