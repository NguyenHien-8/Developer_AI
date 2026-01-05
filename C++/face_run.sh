#!/bin/bash

# Di chuyển vào thư mục build
cd build || exit

# 1. Biên dịch dự án
echo "==== Đang biên dịch FaceApp... ===="
cmake ..
make -j$(nproc)

# Kiểm tra nếu biên dịch thành công
if [ $? -eq 0 ]; then
    echo "==== Biên dịch THÀNH CÔNG. Đang khởi chạy ứng dụng... ===="
    # 2. Quay lại thư mục gốc để nạp assets và models
    cd ..
    ./build/FaceApp
else
    echo "==== Biên dịch THẤT BẠI. Vui lòng kiểm tra lại code C++ ===="
    exit 1
fi