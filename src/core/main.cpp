
#include <iostream>

#include "shmwrapper.h"

int main(int argc, char *argv[]) {
    (void)argc;
    (void)argv;

    ShmWrapper shm;

    //std::cout << shm.getDirection(180).probability << "\n";
    while(true) {
        if(shm.getValid()) { std::cout << "Connected.\n"; break; }
    }

    //std::cout << "Hello, world!\n";
    return 0;
}