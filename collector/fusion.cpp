
#include "config.h"
#include "model.h"

using namespace Recog;

Fusion::Fusion() {
    
    for(auto& key: Config::getSensorKeys()) {
        
        auto conf = Config::getSensorProperities(key);
        sensors_.emplace( key, std::make_shared<HW::Sensor>(
            key,    // name
            conf["orientation"], // orientation
            Geo::Coords::Polar ( // position
                conf["azimuth"], // azimuth
                conf["distance"] // distance
            )
        ));

        Config::registerSensorActualizer( key, getActualizer(key) );
    }


    /*
    const int OMEGA = 50;
    // central sensor
    sensors_.emplace( "C", std::make_shared<HW::Sensor>("C") );
    // left sensor
    sensors_.emplace("L", std::make_shared<HW::Sensor>(
        "L", // name
        50,  // orientation
        Geo::Coords::Polar ( // position
            90+((180-OMEGA)/2.), // azimuth
            sqrt(2*25*25 - 2*25*25*cos(OMEGA/360.*M_PI)) // distance
        )
    ));
    // right sensor
    sensors_.emplace("R", std::make_shared<HW::Sensor>(
        "R", // name
        -50, // orientation
        Geo::Coords::Polar( // position
            -90-((180-OMEGA)/2.), // azimuth
            sqrt(2*25*25 - 2*25*25*cos(-OMEGA/360.*M_PI)) // distance
        )
    ));
    */
}

std::function<void(std::array<int,SEGMENT_SIZE>)> Fusion::getActualizer(std::string sensorkey) {
    std::shared_ptr<HW::Sensor> s = sensors_.at(sensorkey);
    return [s](std::array<int,SEGMENT_SIZE> data){ s->actualizeData(data); };
}

Result Fusion::calculate() {
    // read features from sensors
    Features fc = sensors_.at("C")->readFeatures();
    Features fl = sensors_.at("L")->readFeatures();
    Features fr = sensors_.at("R")->readFeatures();

    Result r;
    /* Do calculations (Features -> Object). */
    /* Not refreshed features are empty. */

    return r;
}