
#include <fstream>
#include <iostream>

#include "extlib/nlohmann/json.hpp"

#include "config.h"

using json = nlohmann::json;

namespace {
    bool init_ = false; 
    std::map<std::string, std::map<std::string, double>> sensors_;
    std::map<std::string, std::function<void(std::array<int,SEGMENT_SIZE>)>> actualizer_;
}

void Config::init() {
    // single call check
    if(init_) throw::std::runtime_error("Config::init() called multiple times.");
    init_ = true;

    // read json
    std::ifstream i("../module/module.conf.json");
    json j;
    try {
        i >> j;
        for(auto& it: j.items()) {
            std::map<std::string, double> val;
            auto d = it.value();
            val.insert( make_pair("distance", d["position"]["distance"]) );
            val.insert( make_pair("azimuth", d["position"]["azimuth"]) );
            val.insert( make_pair("orientation", d["orientation"]) );
            sensors_.insert( make_pair(it.key(), val) );
        }
    } catch(const std::exception& e) {
        std::cerr << "Invalid JSON config file.\n";
        exit(0);
    }
    

}

void checkInited() { if(!init_) throw::std::runtime_error("Config::init() not called."); }

const std::vector<std::string>& Config::getSensorKeys() {
    static std::vector<std::string> v;
    v.empty();
    for(auto &it: sensors_) { v.push_back(it.first); }
    return v;
}

const std::map<std::string, double>& Config::getSensorProperities(const std::string& key) {
    return sensors_.at(key);
}

std::function<void(std::array<int,SEGMENT_SIZE>)> Config::getSensorActualizer(const std::string& s) {
    return actualizer_.at(s);
}

void Config::registerSensorActualizer(const std::string& s, std::function<void(std::array<int,SEGMENT_SIZE>)> actualizer) {
    actualizer_.insert( make_pair(s, actualizer) );
}