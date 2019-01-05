
#include <cstring>
#include <unistd.h>

#include "comm.h"

int main(int argc, char *argv[]) {
    (void)argc;
    (void)argv;

    Comm::MCastServer server;
    const char * hello = "Hello, World!\n";
    do {
        server.send(hello, strlen(hello));
        sleep(1);
    } while(1);
    
}