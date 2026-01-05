#ifndef PROCESSOR_HPP
#define PROCESSOR_HPP

#include <opencv2/opencv.hpp>
#include <algorithm>

class Processor {
public:
    // Hàm này tái hiện logic padding từ file lapcam-facepadding.py 
    static cv::Rect getPaddedRect(cv::Rect face, int imgW, int imgH) {
        // Tỉ lệ padding từ code Python: x(0.1w), y(0.2h) 
        int padX = face.width * 0.1;
        int padY = face.height * 0.2;
        
        // Tính toán tọa độ x1, y1 (sử dụng max để không vượt quá biên 0) 
        int x1 = std::max(face.x - padX, 0);
        int y1 = std::max(face.y - (int)(padY * 0.6), 0); 
        
        // Tính toán tọa độ x2, y2 (sử dụng min để không vượt quá kích thước ảnh) 
        int x2 = std::min(face.x + face.width + padX, imgW);
        int y2 = std::min(face.y + face.height + (int)(padY * 0.6), imgH);
        
        // Trả về vùng chọn đã được mở rộng 
        return cv::Rect(x1, y1, x2 - x1, y2 - y1);
    }

    // Bạn có thể thêm các hàm xử lý khác như Oval Blur ở đây [cite: 58]
};

#endif