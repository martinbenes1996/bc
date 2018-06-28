
/**
 * @file shm.h
 * @brief Shared memory description.
 * 
 * @author Martin Benes.
 */

#ifndef SHM_H
#define SHM_H

#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/shm.h>
#include <sys/types.h>
#include <fcntl.h>

#define CHECK_NONNEGATIVE(i) if((i) < 0) { perror(NULL); abort(); }

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
    bool valid;
    struct Direction space [360]; /**< Sensor space logs. */
    struct Figure figures [256]; /**< Classified figures. */
};

/* ------------ TYPEDEFS ----------------- */
typedef struct Direction Direction;
typedef struct Figure Figure;
typedef struct SharedMemory SharedMemory;
/* --------------------------------------- */

static struct SharedMemory mShm;
static const char * mShmName = "/core2win.shm";

bool mShmCreated = false;
bool isShmCreated() { return mShmCreated; }

int createSharedMemory() {

	// creating new shm
	int shmid = shmget(0, sizeof(struct SharedMemory), IPC_CREAT|IPC_EXCL|0666);
	CHECK_NONNEGATIVE(shmid);
    return shmid;
}
int connectSharedMemory() {
    return shm_open(mShmName, O_RDONLY, 00644);
}
SharedMemory* allocateSharedMemory(int shmid) {
    return (struct SharedMemory *)shmat(shmid, NULL, 0);
}

void closeSharedMemory(int shmid, SharedMemory* p) {
    //if(shm_unlink(mShmName) != 0) abort();

    // remove shared memory
    CHECK_NONNEGATIVE( shmdt(p) );
    CHECK_NONNEGATIVE( shmctl(shmid, IPC_RMID, NULL) );
}

struct Direction getDirection(int azimuth) {
    assert( isShmCreated() ); 
    assert(azimuth >= 0 && azimuth < 360);
    return mShm.space[azimuth];
}
struct Figure getFigure(int figure) {
    assert( isShmCreated() );
    assert(figure >= 0 && figure < 256);
    return mShm.figures[figure];
}


#endif // SHM_H