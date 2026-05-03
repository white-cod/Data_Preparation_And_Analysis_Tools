cmake_minimum_required(VERSION 3.10)
project(lab_07)

set(CMAKE_CXX_STANDARD 17)

find_package(OpenCV REQUIRED)

add_executable(lab_07 main.cpp)
target_link_libraries(lab_07 ${OpenCV_LIBS})
