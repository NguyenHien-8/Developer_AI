#!/bin/bash

echo "--- SETUP C++ VOICE SYSTEM ---"

# 1. Cài đặt các gói phụ thuộc hệ thống (PortAudio, CURL)
echo "[1/3] Checking system dependencies..."
sudo apt update
sudo apt install -y cmake g++ libportaudio2 portaudio19-dev libcurl4-openssl-dev mpg123

# 2. Tạo thư mục build
echo "[2/3] Preparing build directory..."
mkdir -p build
cd build

# 3. Chạy CMake và Biên dịch
echo "[3/3] Compiling VoiceOrder..."
cmake ..
make

echo "----------------------------------------"
echo "C++ BUILD COMPLETED!"
echo "Make sure your Relay Server (Node.js) is running on port 8085 before starting."