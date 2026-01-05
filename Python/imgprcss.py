import cv2
from tensorflow.keras.preprocessing.image import img_to_array

# Ảnh 1
face_img1 = cv2.imread("d.png")
rgb_img1 = cv2.cvtColor(face_img1, cv2.COLOR_BGR2RGB)
gray1 = cv2.cvtColor(rgb_img1, cv2.COLOR_RGB2GRAY)
blurred1 = cv2.GaussianBlur(gray1, (3, 3), 0)
darker1 = cv2.convertScaleAbs(blurred1, alpha=0.7, beta=-10)
equalized1 = cv2.equalizeHist(darker1)

# Ảnh 2
face_img2 = cv2.imread("l.png")
rgb_img2 = cv2.cvtColor(face_img2, cv2.COLOR_BGR2RGB)
gray2 = cv2.cvtColor(rgb_img2, cv2.COLOR_RGB2GRAY)
blurred2 = cv2.GaussianBlur(gray2, (3, 3), 0)
darker2 = cv2.convertScaleAbs(blurred2, alpha=0.7, beta=-10)
equalized2 = cv2.equalizeHist(darker2)

# Resize về cùng kích thước nếu chưa bằng nhau
equalized1 = cv2.resize(equalized1, (400, 400))
equalized2 = cv2.resize(equalized2, (400, 400))

# Nối ngang 2 ảnh để hiển thị
combined = cv2.hconcat([equalized1, equalized2])

# Hiển thị
cv2.imshow("So sánh ảnh đã xử lý", combined)
cv2.waitKey(0)
cv2.destroyAllWindows()