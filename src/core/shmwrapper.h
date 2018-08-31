#ifndef SHMWRAPPER_H
#define SHMWRAPPER_H

#include <cassert>
#include <dlfcn.h>
#include <iostream>

#include "shm.h"

class ShmWrapper {
    public:
        ShmWrapper();
        ~ShmWrapper();

        Direction& getDirection(int azimuth) { 
            assert((azimuth >= 0) && (azimuth < 360)); 
            return mShm->space[azimuth]; 
        }
        Figure& getFigure(int figure) { 
            assert((figure >= 0) && (figure < 256));
            return mShm->figures[figure]; 
        }
        bool getValid() { return mShm->valid; }

    private:
        void *mLibHandle = NULL;
        int mShmHandle = -1;
        SharedMemory *mShm = NULL;
        void(*mCloseShm)(int, SharedMemory*);
};

ShmWrapper::ShmWrapper() {
    // open shared library
    mLibHandle = dlopen("/home/martin/bc/src/libglobals.so", RTLD_LAZY);
    if (!mLibHandle) {
        std::cerr << "Can't find libglobals.so.\n";
        exit(1);
    }
    dlerror();

    // load library functions
    int(*createShm)() = (int(*)())dlsym(mLibHandle, "createSharedMemory");
    SharedMemory*(*allocShm)(int) = (SharedMemory*(*)(int))dlsym(mLibHandle, "allocateSharedMemory");
    mCloseShm = (void(*)(int, SharedMemory *))dlsym(mLibHandle, "closeSharedMemory");
    dlerror();

    // initialize shm
    mShmHandle = createShm();
    mShm = allocShm(mShmHandle);

    //std::cerr << "Shm created!\n";
}

ShmWrapper::~ShmWrapper() {
    // close shm
    mCloseShm(mShmHandle, mShm);
    // close shared library
    dlclose(mLibHandle);
    dlerror();

    //std::cerr << "Shm closed!\n";
}

#endif // SHMWRAPPER_H