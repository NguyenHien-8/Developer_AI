import cv2
from keras._tf_keras.keras.applications.mobilenet_v2 import MobileNetV2



# MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
MODEL_MEAN_VALUES = (104.0, 117.0, 123.0) 

age_list = ['(0,2)','(4,6)','(8,12)','(15,20)','(25,32)','(38,43)','(48,53)','(60,100)']
gender_list = ['Male','Female']

def initialize_model():
    print('Loading models...')
    gender_net = cv2.dnn.readNetFromCaffe("models/genderp.prototxt","models/gender.caffemodel")
    return (gender_net)

def ga_predict(face_img, gender_net):
    print('predict...')
    blob = cv2.dnn.blobFromImage(face_img, 1, (224,224), MODEL_MEAN_VALUES, swapRB=False)
    print(blob.shape)
    gender_net.setInput(blob)
    
    gender_preds = gender_net.forward()
    gender = gender_list[gender_preds[0].argmax()]
    return (gender)


# def initialize_model():
    # model = MobileNetV2(weights="imagenet")
    # model.summary()
    
# initialize_model()
    