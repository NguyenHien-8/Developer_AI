import cv2
import tensorflow as tf
from keras._tf_keras.keras.applications.mobilenet_v2 import MobileNetV2
from keras._tf_keras.keras.preprocessing.image import load_img, img_to_array
from keras._tf_keras.keras.models import load_model
from keras._tf_keras.keras.saving import register_keras_serializable
import keras

@register_keras_serializable(package="Custom", name="repeat_channels")
def repeat_channels(img):
    return tf.tile(img, [1, 1, 1, 3])

custom_objects = {"repeat_channels": repeat_channels}
keras.config.enable_unsafe_deserialization()
model = load_model('assets/ga_model (3).keras', custom_objects=custom_objects)

def result_process(pred):
    gender_dict= {0:"male", 1:"female"}
    a= pred[1][0][0]
    gender = a
    # if a>0.3:
    #     a=1
    # else:
    #     a=0
    # print(a)
    # gender = gender_dict[a]
    age = round(pred[0][0][0])
    return age, gender
    
def predict_ga(face_img):
    rgb_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2GRAY)
    img = cv2.resize(img, (128, 128))
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    img = img_to_array(img)
    img = img.reshape(1,128,128,1)
    img = img/255.0
    pred = model.predict(img)
    pred = result_process(pred)
    return pred
