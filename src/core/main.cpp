
#include <iostream>

#include "shmwrapper.h"

int main(int argc, char *argv[]) {
    (void)argc;
    (void)argv;

    ShmWrapper shm;

    std::cout << shm.getDirection(180).probability << "\n";


    //std::cout << "Hello, world!\n";
    return 0;
}