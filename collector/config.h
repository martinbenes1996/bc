#ifndef _CONFIG_H_
#define _CONFIG_H_

#include <functional>
#include <map>
#include <string>
#include <vector>

#include "globals.h"

namespace Config {
    void init();

    const std::vector<std::string>& getSensorKeys();
    const std::map<std::string, double>& getSensorProperities(const std::string&);
    
    std::function<void(std::array<int,SEGMENT_SIZE>)> getSensorActualizer(const std::string&);
    void registerSensorActualizer(const std::string&, std::function<void(std::array<int,SEGMENT_SIZE>)>);
}

#endif // _CONFIG_H_