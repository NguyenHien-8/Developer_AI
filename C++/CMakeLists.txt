cmake_minimum_required(VERSION 3.10)
project(VoiceOrder)

set(CMAKE_CXX_STANDARD 17)

find_package(CURL REQUIRED)
find_package(nlohmann_json REQUIRED)
find_package(Threads REQUIRED)

include_directories(include)
include_directories(/usr/local/include) # Cho RapidFuzz và IXWebSocket

set(SOURCES
    src/main.cpp
    src/state_machine.cpp
    src/database.cpp
)

add_executable(VoiceOrder ${SOURCES})

# Đã thêm portaudio và sửa đường dẫn libvosk.so
target_link_libraries(VoiceOrder PRIVATE
    ${CURL_LIBRARIES}
    nlohmann_json::nlohmann_json
    ixwebsocket
    portaudio       # THÊM DÒNG NÀY ĐỂ HẾT LỖI
    ssl
    crypto
    z
    Threads::Threads
    dl
    "${CMAKE_CURRENT_SOURCE_DIR}/third_party/libvosk.so"
)