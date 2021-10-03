cmake_minimum_required(VERSION 3.1)
project(testopenexr_exe LANGUAGES CXX)

find_package(OpenEXR REQUIRED)

add_executable(${PROJECT_NAME} testopenexr.cpp)

target_include_directories(${PROJECT_NAME} PRIVATE ${OPENEXR_INCLUDE_DIRS})

target_link_libraries(${PROJECT_NAME} ${OPENEXR_LIBRARIES})
