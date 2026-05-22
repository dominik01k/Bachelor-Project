#include "Config.h"
#include <iostream>
#include <string>
#include "Game.h"
#include "PythonEnvironment.h"
#include "MLDataCollector.h"
#include "Logger.h"

int main(int argc, char* argv[]) {
    
    g_config.loadFromArgs(argc, argv);

    Logger::init();

    PythonEnvironment::initialize();
    
    {
        Game game;
        game.run();
    }

    PythonEnvironment::finalize();
    return 0;
}