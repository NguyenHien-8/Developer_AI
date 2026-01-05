MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)

age_list = ['(0,2)','(4,6)','(8,12)','(15,20)','(25,32)','(38,43)','(48,53)','(60,100)']
gender_list = ['Male','Female']

def initialize_model():
    print('Loading models...')
    age_net = cv2.dnn.readNetFromCaffe("models/deploy_age2.prototxt", "models/age_net.caffemodel")  
    gender_net = cv2.dnn.readNetFromCaffe("models/deploy_gender2.prototxt","models/gender_net.caffemodel")
    return (age_net, gender_net)

def ga_predict(face_img, age_net, gender_net):
    print('predict...')
    blob = cv2.dnn.blobFromImage(face_img, 1, (227,227), MODEL_MEAN_VALUES, swapRB=False)
    print(blob.shape)
    gender_net.setInput(blob)
    
    gender_preds = gender_net.forward()
    gender = gender_list[gender_preds[0].argmax()]
    age_net.setInput(blob)
    age_preds = age_net.forward()
    age = age_list[age_preds[0].argmax()]    
    return (age, gender)
