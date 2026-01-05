import time
import cv2
import os
import sys
sys.path.append(os.path.abspath("../G&A_DETECTION/"))
from utils.mh_c import ga_predict, initialize_model

def capture_loop():  
    face_cascade = cv2.CascadeClassifier('assets/haarcascade_frontalface_alt.xml')
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Không thể mở camera!")
        exit()
       
    gender_net = initialize_model()
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # faces = face_cascade.detectMultiScale(gray,1.1,5)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=7, minSize=(30, 30))
        # print("found "+str(len(faces))+"faces")
        
        for (x,y,w,h) in faces:
            cv2.rectangle(frame, (x,y),(x+w,y+h),(255,255,0),2 )
            face_img = frame[y:y+h, x:x+w].copy()
            gender = ga_predict(face_img, gender_net)
            print(gender)
        
        cv2.imshow("OK", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):  
            break
    camera.release()
    cv2.destroyAllWindows()
      
capture_loop()