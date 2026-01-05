import time
import cv2
import os
import sys
import face_recognition
import numpy as np
sys.path.append(os.path.abspath("../G&A_DETECTION/"))
from utils.ga_model_handle import predict_ga

known_encodings = []
threshold = 0.6

def is_new_face(encoding):
    if not known_encodings:
        return True
    distances = face_recognition.face_distance(known_encodings, encoding) #what's that?
    return np.min(distances)>threshold

def capture_loop():  
    # face_cascade = cv2.CascadeClassifier('assets/haarcascade_frontalface_alt.xml')
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Không thể mở camera!")
        exit()
    frame_count = 0
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        
        frame_count += 1
        if frame_count % 2 == 0:
            continue 
        
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(gray)
        face_encodings = face_recognition.face_encodings(gray, face_locations)
 
        for (top, right, bottom, left), encoding in zip(face_locations,face_encodings):
            if is_new_face(encoding):
                face_img = frame[top:bottom, left:right].copy()
                age, gender = predict_ga(face_img)
                # print(result)
                known_encodings.append(encoding)
            cv2.rectangle(frame, (left,top),(right,bottom),(0,255,255),3)
        
        cv2.imshow(f"{age, gender}",frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):  
            break
    camera.release()
    cv2.destroyAllWindows()
      
capture_loop()