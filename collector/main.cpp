
#include <cstring>
#include <unistd.h>

#include "comm.h"
#include "config.h"
#include "model.h"

int main(int argc, char *argv[]) {
    (void)argc;
    (void)argv;

    Config::init();

    // initialize multicast server
    Comm::MCastServer server;
    Recog::Object o;
    o.azimuth = -50;
    o.distance = 35;

    // fusion engine
    Recog::Fusion fusion;

    // initialize listener
    Comm::Listener listener;


    
    // main loop
    do {

        try {
        
            // calculate
            /*
            Recog::Result result = fusion.calculate();
            std::cerr << result.bufferSize() << "\n";
            server.send(result.toBuffer(), result.bufferSize());
            */

            /* --- DELETE --- */
            int sampledata[] = { 2/* two objects */,
                                    /* first: azimuth 0, distance 10 */0,100,
                                    /* second: azimuth 90, distance 15 */-45,150, };
            server.send(sampledata, 5*sizeof(int));
            /* -------------- */

        // error
        } catch(Comm::Exception& e) { std::cerr << e.what() << "\n"; }
        
        sleep(1);
    } while(1); 

}