import time
import cv2
import os
import sys
sys.path.append(os.path.abspath("../G&A_DETECTION/"))
from utils.model_handle import ga_predict, initialize_model

def capture_loop():  
    face_cascade = cv2.CascadeClassifier('assets/haarcascade_frontalface_alt.xml')
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Không thể mở camera!")
        exit()
       
    age_net, gender_net = initialize_model()
    face_labels = []
    
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # faces = face_cascade.detectMultiScale(gray,1.1,5)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=7, minSize=(30, 30))
        # print("found "+str(len(faces))+"faces")
        current_labels = []
        for (x,y,w,h) in faces:
            cv2.rectangle(frame, (x,y),(x+w,y+h),(255,255,0),2 )
            face_img = frame[y:y+h, x:x+w].copy()
            age, gender = ga_predict(face_img, age_net, gender_net)
            # print(age, gender)
            label = f"{gender}, {age}"
            current_labels.append((x,y,label))
        else:
                for (lx, ly, ltext) in face_labels:
                    if abs(x-lx) < 20 and abs (y-ly)<20:
                        label = ltext
                        current_labels.append((x,y,label))
                        break
        for (x, y, label) in current_labels:
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("OK", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):  
            break
    camera.release()
    cv2.destroyAllWindows()
      
capture_loop()