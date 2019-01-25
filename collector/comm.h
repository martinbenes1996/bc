#ifndef _COMM_H_
#define _COMM_H_

#include <arpa/inet.h>
#include <cstdio>
#include <cstring>
#include <exception>
#include <functional>
#include <iostream>
#include <netinet/in.h>
#include <string>
#include <sys/types.h>
#include <sys/socket.h>
#include <thread>

#include "config.h"
#include "model.h"

namespace Comm {
    class Exception {
        public:
            Exception(const char *msg) { msg_ = msg; }
            std::string what() { return std::string(msg_); }
        private:
            const char * msg_;
    };
    
    class Server {
        public:
            Server() {
                sock_ = socket(AF_INET, SOCK_DGRAM, 0);
                if(sock_ < 0) { throw Exception("Comm::Server: socket() failed."); }

                struct sockaddr_in server_address, client_address;
                memset(&server_address, 0, sizeof(server_address));
                memset(&client_address, 0, sizeof(client_address));
                
                bcaster_ = new std::thread([this](){ this->addressToClients(); });
            }

            ~Server() {
                bcaster_->join();
            }

            void addressToClients() {
                int bcast_sock;
                bcast_sock = socket(AF_INET, SOCK_DGRAM, 0);
                if(bcast_sock < 0) { throw Exception("Comm::Server: socket() failed."); }

                int bcast = 1;
                int bcaststatus = setsockopt(bcast_sock, SOL_SOCKET, SO_BROADCAST, &bcast, sizeof(bcast));
                if(bcaststatus < 0) { throw Exception("Comm::Server: setsockopt() failed."); }

                struct sockaddr_in server, from;
                unsigned fromsize = sizeof(from);
                memset(&server, 0, sizeof(server));
                server.sin_family = AF_INET;
                server.sin_addr.s_addr = INADDR_ANY;
                server.sin_port = htons(12345);

                int bindstatus = bind(bcast_sock, (struct sockaddr *)&server, sizeof(server));
                if(bindstatus < 0) { throw Exception("Comm::Server: bind() failed."); }

                const unsigned messagelen = 14;
                char buffer[messagelen+1];

                do {
                    std::cout << "Listening for clients...\n";
                    int recvsize = recvfrom(bcast_sock, buffer, messagelen, 0, (struct sockaddr *)&from, &fromsize);
                    if(recvsize < 13) { throw Exception("Comm::Server: recvfrom() failed."); }

                    unsigned short port = ntohs(*(unsigned short *)(buffer + 11));
                    std::cout << "Received " << recvsize << "B: " << std::string(buffer).substr(0,11) << ": " << port << "\n";
                } while(1);
            }


        private:
            int sock_;
            std::thread * bcaster_;     
    };

    class MCastServer {
        public:
            MCastServer() {
                sock_ = socket(AF_INET, SOCK_DGRAM, 0);
                if(sock_ < 0) { throw Exception("Comm::MCastServer: socket() failed."); }

                memset(&server_, 0, sizeof(server_));
                server_.sin_family = AF_INET;
                server_.sin_addr.s_addr = inet_addr("224.0.0.128");
                server_.sin_port = htons(12345);
            }

            void send(void * d, size_t size) {
                std::cout << "Comm::MCastServer: sending update to " << inet_ntoa(server_.sin_addr) << ":" << ntohs(server_.sin_port) << "\n";
                int sent = sendto(sock_, d, size, 0, (struct sockaddr*)&server_, sizeof(server_));
                if(sent < 0) { std::cerr << errno << "\n"; throw Exception("Comm:MCastServer: sendto() failed."); }
            }

        private:
            int sock_;
            struct sockaddr_in server_;
    };

    class Listener {
        public:
            Listener() {
                sock_ = socket(AF_INET, SOCK_DGRAM, 0);
                if(sock_ < 0) { throw Exception("Comm::Server: socket() failed."); }

                listen_async();
            }

            ~Listener() { if(!listener_) listener_->join(); }

            void listen_async() {
                listener_ = new std::thread([this](){ this->listen(); });
            }

            void listen() {

                struct sockaddr_in server, from;
                unsigned fromsize = sizeof(from);
                memset(&server, 0, sizeof(server));
                server.sin_family = AF_INET;
                server.sin_addr.s_addr = INADDR_ANY;
                server.sin_port = htons(5005);

                int bindstatus = bind(sock_, (struct sockaddr *)&server, sizeof(server));
                if(bindstatus < 0) { throw Exception("Comm::Server: bind() failed."); }

                char segment[2*SEGMENT_SIZE + 16];
                std::cout << "Comm::Listener: UDP waiting for connection.\n";

                while(true) {
                    
                    unsigned recvsize = recvfrom(sock_, segment, 2*SEGMENT_SIZE + 16, 0, (struct sockaddr *)&from, &fromsize);
                    if(recvsize < 2*SEGMENT_SIZE) { throw Exception("Comm::Server: recvfrom() failed."); }

                    char sensorname[16];
                    strncpy(sensorname, segment, 16);
                    if(sensorname[15] != 0) { std::cerr << "Invalid data!\n"; continue; }
                    char *data = segment + strlen(sensorname)+1;

                    std::array<int, SEGMENT_SIZE> a;
                    for(int i = 0; i < SEGMENT_SIZE*2; i += 2) {
                        unsigned r = (data[0] << 8) | (0xFF & data[1]);
                        a.at(i/2) = r;                        
                    }

                    try {
                        Config::getSensorActualizer( std::string(sensorname) )( a );
                    } catch(const std::exception& e) {
                        std::cerr << "Invalid data!\n"; continue;
                    }
                    
                    std::cout << "Comm::Listener: Received " << recvsize << " B.\n";
                }
            }

        private:
            int sock_;
            std::thread * listener_;
    };
}

#endif // _COMM_H_