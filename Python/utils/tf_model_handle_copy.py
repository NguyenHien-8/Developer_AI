import cv2
import tensorflow as tf
# import tflite_runtime.interpreter as tflite
import numpy as np


# interpreter = tf.lite.Interpreter(model_path="assets/gamodel.tflite")
interpreter = tf.lite.Interpreter(model_path="assets/ga01.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def result_process(age_pred, gender_pred):
    gender_dict= {0:"male", 1:"female"}
    age = age_pred[0][0]
    age = round(age)
    gender = gender_pred[0][0]
    if gender > 0.5 :
        gender = 1
    else :
        gender = 0
    gender = gender_dict[gender]
    return age, gender
    
def lite_predict_ga(face_img):
    rgb_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    darker = cv2.convertScaleAbs(blurred, alpha=0.7, beta=-10)
    equalized = cv2.equalizeHist(darker)
    img = cv2.resize(equalized, (128, 128))
    img = np.array(img, dtype=np.float32)
    img = img.reshape(1, 128, 128, 1)
    img = img/255.0
    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()
    gender_pred = interpreter.get_tensor(output_details[0]['index'])
    age_pred = interpreter.get_tensor(output_details[1]['index'])
    print(age_pred,gender_pred)
    pred = result_process(age_pred, gender_pred)
    return pred


