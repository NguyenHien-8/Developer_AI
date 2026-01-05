cmake_minimum_required(VERSION 3.10)
project(FaceRecognition)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")

find_package(OpenCV REQUIRED)
find_package(Threads REQUIRED)

# Tìm thư viện IXWebSocket
find_library(IXWEBSOCKET_LIB ixwebsocket)

include_directories(${OpenCV_INCLUDE_DIRS})

add_executable(FaceApp src/main.cpp)

target_link_libraries(FaceApp 
    ${OpenCV_LIBRARIES} 
    Threads::Threads
    ${IXWEBSOCKET_LIB}
    ssl
    crypto
    z
)