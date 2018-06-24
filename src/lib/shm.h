
/**
 * @file shm.h
 * @brief Shared memory description.
 * 
 * @author Martin Benes.
 */

#ifndef SHM_H
#define SHM_H

#include <stdbool.h>

/**
 * @brief Direction log of the sensor.
 */
struct Direction {
    bool valid; /**<  Whether the data is valid. */

    int azimuth; /**< Azimuth of the direction. */

    double value; /**< Value of the signal in the direction. */
    double temperature; /**< Approximate temperature. */

    double probability; /**< Probability of the figure. */
    double score; /**< Soft max score. */
};

/**
 * @brief Classified figure.
 */
struct Figure {
    bool valid; /**< Whether the data is valid. */

    int azimuth; /**< Azimuth of the figure to the sensor. */
    double distance; /**< Distance of the figure to the sensor. */

    double temperature; /**< Temperature of the figure. */

    double probability; /**< Probability of the presence of the figure. */
    double score; /**< Soft max score of the presence of the figure. */
};

/**
 * @brief Shared memory structure.
 */
struct SharedMemory {
    struct Direction space [360]; /**< Sensor space logs. */
    struct Figure figures [255]; /**< Classified figures. */
};

/* ------------ TYPEDEFS ----------------- */
typedef struct Direction Direction;
typedef struct Figure Figure;
typedef struct SharedMemory SharedMemory;
/* --------------------------------------- */

#endif // SHM_H