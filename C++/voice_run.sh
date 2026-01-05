#!/bin/bash

echo "--- STARTING C++ VOICE ENGINE ---"

# Xác định thư mục hiện tại
PROJECT_ROOT=$(pwd)

# 1. Thiết lập LD_LIBRARY_PATH để chương trình tìm thấy libvosk.so
# Bao gồm đường dẫn third_party và thư viện hệ thống
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PROJECT_ROOT/third_party:/usr/local/lib

# 2. Kiểm tra xem file thực thi có tồn tại không
if [ ! -f "./build/VoiceOrder" ]; then
    echo "Error: VoiceOrder executable not found. Please run ./voice_lib.sh first."
    exit 1
fi

# 3. Chạy chương trình
echo "Voice Engine is connecting to ws://localhost:8085/voice..."
./build/VoiceOrder