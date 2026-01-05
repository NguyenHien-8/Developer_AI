import cv2
import tensorflow as tf
import numpy as np
import os
from collections import Counter

age_interpreter = None
age_input_details = None
age_output_details = None

def load_age_model():
    global age_interpreter, age_input_details, age_output_details
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, '..', 'models', 'ageModel.tflite')
    age_interpreter = tf.lite.Interpreter(model_path=model_path)
    age_interpreter.allocate_tensors()
    age_input_details = age_interpreter.get_input_details()
    age_output_details = age_interpreter.get_output_details()
    
def age_predict(face_img):
    rgb_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    darker = cv2.convertScaleAbs(blurred, alpha=0.7, beta=-10)
    equalized = cv2.equalizeHist(darker)
    img = cv2.resize(equalized, (160, 160))
    img = np.array(img, dtype=np.float32).reshape(1, 160, 160, 1) / 255.0

    age_interpreter.set_tensor(age_input_details[0]['index'], img)
    age_interpreter.invoke()
    age_pred = age_interpreter.get_tensor(age_output_details[1]['index'])
    age = round(age_pred[0][0])
    print(age)
    return age

def find_most_common_age_group(ages):
    age_groups = [age // 10 for age in ages]
    group_counts = Counter(age_groups)
    most_common_group, _ = group_counts.most_common(1)[0]
    return most_common_group
