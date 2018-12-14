
#include <iostream>

#include "socket.h"

int main() {
    // open socket
    ClientSocket s;
    if( !s.connectToServer() ) return 1;

    std::cout << "Hello, World!\n";
    return 0;
}