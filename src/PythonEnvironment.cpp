#include "PythonEnvironment.h"
#include <Python.h>
#include <iostream>
#include "Logger.h"

void PythonEnvironment::initialize() {
    if (!Py_IsInitialized()) {
        Py_Initialize();
        PyRun_SimpleString("import sys");
        PyRun_SimpleString("sys.path.insert(0, '/Users/dominik/Documents/Universität/8.Semester/Bachelorarbeit/Game Kopie/venv/lib/python3.13/site-packages')");
        PyEval_InitThreads();
        PyEval_SaveThread();
        LOG_INFO("Setup", "Python initialized");
    }
}

void PythonEnvironment::finalize() {
    if (Py_IsInitialized()) {
        Py_Finalize();
        LOG_INFO("Setup", "Python finalized");
    }
}
