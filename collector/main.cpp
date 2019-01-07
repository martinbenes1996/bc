
#include <cstring>
#include <unistd.h>

#include "comm.h"
#include "model.h"

int main(int argc, char *argv[]) {
    (void)argc;
    (void)argv;

    /*
    Comm::MCastServer server;
    Recog::Object o;
    o.azimuth = -50;
    o.distance = 35;
    
    do {
        server.send(&o, sizeof(o));
        sleep(1);
    } while(1);
    */

    /*
    HW::Sensor s("MujSensor");
    Recog::Features f = s.readFeatures();
    
    for(auto &i: f.data) { std::cout << i << " "; }
    std::cout << "\n";
    */

    
    
    Comm::Listener listener;
    Recog::Fusion fusion;
    listener.listen_async( fusion.getActualizer("C") );

    do {
        Recog::Result result = fusion.calculate();
        result.log();
    } while(getchar() != EOF);
    

}