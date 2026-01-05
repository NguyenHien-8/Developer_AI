import cv2
import tensorflow as tf
# import tflite_runtime.interpreter as tflite
import numpy as np
import matplotlib.pyplot as plt
import os

# interpreter = tf.lite.Interpreter(model_path="models/gender_oval_blur.tflite")
# interpreter.allocate_tensors()

# gender_input_details = interpreter.get_gender_input_details()
# output_details = interpreter.get_output_details()

gender_interpreter = None
gender_input_details = None
gender_output_details = None

def load_gender_model():
    global gender_interpreter, gender_input_details, gender_output_details
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, '..', 'models', 'gender_oval_blur.tflite')
    # model_path = os.path.join(base_dir, '..', 'models', 'gender_retrain.tflite')
    gender_interpreter = tf.lite.Interpreter(model_path=model_path)
    gender_interpreter.allocate_tensors()
    gender_input_details = gender_interpreter.get_input_details()
    gender_output_details = gender_interpreter.get_output_details()

def hair_img_prepare(img, x, y, w, h):
    padding_x = int(w * 0.2)
    padding_y = int(h * 0.5)
    x1 = max(x - padding_x, 0)
    y1 = max(y - int(padding_y * 0.6), 0)
    x2 = min(x + w + int(padding_x * 0.6), img.shape[1])
    y2 = min(y + h + int(padding_y * 0.3), img.shape[0])
    face_region = img[y:y+h, x:x+w]
    blurred_face = cv2.GaussianBlur(face_region, (99, 99), 30)
    mask = np.zeros((h, w), dtype=np.uint8) 
    center = (w // 2, h // 2)
    axes = (int(w * 0.4), int(h * 0.5))  
    cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
    mask_3ch = cv2.merge([mask, mask, mask])
    face_with_blur = np.where(mask_3ch == 255, blurred_face, face_region)
    img[y:y+h, x:x+w] = face_with_blur
    full_face_hair_img = img[y1:y2, x1:x2].copy()
    return full_face_hair_img
    
def gender_predict(img, x, y, w, h):
    face_img = hair_img_prepare(img, x, y, w, h)
    
    gray = cv2.cvtColor(face_img, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    darker = cv2.convertScaleAbs(blurred, alpha=0.7, beta=-10)
    equalized = cv2.equalizeHist(darker)
    img = cv2.resize(equalized, (160, 160))
    cv2.imshow('proccessed',img)
    cv2.waitKey(1)
    
    img = np.array(img, dtype=np.float32)
    img = img.reshape(1, 160, 160, 1)
    img = img/255.0
    
    gender_interpreter.set_tensor(gender_input_details[0]['index'], img)
    gender_interpreter.invoke()
    gender_pred = gender_interpreter.get_tensor(gender_output_details[0]['index'])
    gender_pred = gender_pred[0][0]
    return gender_pred

