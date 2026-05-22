cmake_minimum_required(VERSION 3.10)
project(GameProject)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)

FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11.git
    GIT_TAG v2.12.0
)

FetchContent_MakeAvailable(pybind11)


if(APPLE)
    message(STATUS "Configuring for macOS")

    set(SFML_ROOT "${CMAKE_SOURCE_DIR}/external/sfml/macOS")
    set(SFML_DIR "${SFML_ROOT}/lib/cmake/SFML")


elseif(WIN32)
    message(STATUS "Configuring for Windows")

    set(SFML_ROOT "${CMAKE_SOURCE_DIR}/external/sfml/windows")
    set(SFML_DIR "${SFML_ROOT}/lib/cmake/SFML")

else()
    message(FATAL_ERROR "Unsupported platform")
endif()

find_package(SFML 3 REQUIRED COMPONENTS Graphics Audio Network)

add_library(imgui
    external/imgui/imgui.cpp
    external/imgui/imgui_draw.cpp
    external/imgui/imgui_tables.cpp
    external/imgui/imgui_widgets.cpp
    external/imgui/imgui_demo.cpp

    external/imgui-sfml/imgui-SFML.cpp
)


target_include_directories(imgui PUBLIC
    external/imgui
    external/imgui-sfml
    ${SFML_ROOT}/include
)

file(GLOB_RECURSE SOURCE_FILES
    src/*.cpp
)
add_executable(GameProject ${SOURCE_FILES})


target_link_libraries(GameProject SFML::Graphics SFML::Audio SFML::Network imgui pybind11::embed)

if(APPLE)
    target_link_libraries(GameProject
        "-framework OpenGL"
    )
endif()

target_include_directories(GameProject PRIVATE 
    include/header
    include/json/single_include
    external/imgui              
    external/imgui-sfml
    ${SFML_ROOT}/include  
)


if (APPLE)
    message(STATUS "Configuring for macOS")
    set(PYTHON_RUNTIME_DIR "${CMAKE_SOURCE_DIR}/external/python/macOS")
    target_link_directories(GameProject PRIVATE "${PYTHON_RUNTIME_DIR}")
    target_link_libraries(GameProject "${PYTHON_RUNTIME_DIR}/libpython3.13.dylib")
    target_include_directories(GameProject PRIVATE "${PYTHON_RUNTIME_DIR}/include")
elseif(WIN32)
    message(STATUS "Configuring for Windows")
    set(PYTHON_RUNTIME_DIR "${CMAKE_SOURCE_DIR}/external/python/windows")
    target_link_directories(GameProject PRIVATE "${PYTHON_RUNTIME_DIR}")
    target_link_libraries(GameProject "${PYTHON_RUNTIME_DIR}/python3.dll")
    target_include_directories(GameProject PRIVATE "${PYTHON_RUNTIME_DIR}/include")
endif()

set(REQUIREMENTS_FILE "${CMAKE_SOURCE_DIR}/requirements.txt")
set(VENV_DIR "${CMAKE_BINARY_DIR}/venv")

if(EXISTS ${REQUIREMENTS_FILE})
    if(APPLE)
        set(PIP_EXECUTABLE "${VENV_DIR}/bin/pip")
    elseif(WIN32)
        set(PIP_EXECUTABLE "${VENV_DIR}/Scripts/pip.exe")
    endif()

    add_custom_target(install_python_requirements
        COMMAND ${PYTHON_EXECUTABLE} -m venv ${VENV_DIR}
        COMMAND ${PIP_EXECUTABLE} install --upgrade pip
        COMMAND ${PIP_EXECUTABLE} install -r ${REQUIREMENTS_FILE}
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        COMMENT "Creating venv and installing Python dependencies from requirements.txt"
        VERBATIM
    )

    add_dependencies(GameProject install_python_requirements)
endif()

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -stdlib=libc++ -Wno-deprecated-declarations")
