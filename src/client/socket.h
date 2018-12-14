
#include <errno.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <stdlib.h>

// address of server, program connects to
#define SERVER_ADDRESS "127.0.0.1"

/**
 * @brief Client Socket Wrapper.
 */
class ClientSocket {
    public:
        /**
         * @brief Connects to the server.
         * @returns True, if success. False if fail.
         */
        bool connectToServer() {
            // open socket
            serverSocket = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP);
            if(serverSocket == -1) {
                return closeSocket("connect failure");
            }
            std::cerr << "Ahoj!\n";

            // fill sockaddr
            struct sockaddr_in sa;
            memset(&sa, 0, sizeof(sa));
            sa.sin_family = AF_INET;
            sa.sin_addr.s_addr = inet_pton(AF_INET, SERVER_ADDRESS, &sa.sin_addr);
            sa.sin_port = htons(7654);

            // connect
            if( connect(serverSocket, (struct sockaddr *)&sa, sizeof(sa)) == -1 ) {
                return closeSocket("connect failure");
            }

            return true;
        }

        /**
         * @brief Destructor. Closes the socket.
         */
        ~ClientSocket() {
            if(serverSocket != -1) shutdown(serverSocket, SHUT_RDWR);
        }

    private:
        int serverSocket = -1;

        bool closeSocket(const char * msg) {
            perror(msg);
            if(serverSocket != -1) close(serverSocket);
            return false;
        }

};
