## COMPONENT TEST FILE 
# 24/04 10:16pm
# read laptop's front camera
# this file is for testing using average value on gender prediction
# using [gender_oval_blur.tflite]
# up to this point, the predict result is correct at almost the time

import cv2
import os
import sys
import numpy as np
# sys.path.append(os.path.abspath("../G&A_DETECTION/"))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.gender_model_with_average import hair_img_prepare, gender_predict
    

def capture_loop():  
    face_cascade = cv2.CascadeClassifier('assets/haarcascade_frontalface_alt.xml')
    camera = cv2.VideoCapture(0)

    frame_count = 0
    # invoke the model to predict every 5 frames
    # get the average of 10 times prediction
    process_every_n_frames =5
    gender_el_count = 15
    
    if not camera.isOpened():
        print("Fail to open camera")
        exit()
    
    face_labels = []
    gender_average = []
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        frame = cv2.flip(frame,1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # faces detection
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=7, minSize=(30, 30))
        current_labels = []
        
        for (x,y,w,h) in faces:
            # cv2.rectangle(frame, (x,y),(x+w,y+h),(255,255,0),1)
            
            if frame_count % process_every_n_frames ==0:
                full_frame = frame.copy()
                full_head_img = hair_img_prepare(full_frame, x, y, w, h)
                gender = gender_predict(full_head_img)
                # face_img = frame[x:x+w, y:y+h].copy()
                # age, gender = lite_predict_ga(face_img)
                # print(a)
                
                # cv2.rectangle(frame, (x,y),(x+w,y+h),(255,255,0),3)
                
                gender_average.append(gender)
                if len(gender_average) == gender_el_count:
                    avg_gender = sum(gender_average)/gender_el_count
                    genderstr = str(avg_gender)
                    print(f"HEHEHE {genderstr}")
                    current_labels.append((x,y,genderstr))
                    gender_average = []
            else:
                for (lx, ly, ltext) in face_labels:
                    if abs(x-lx) < 20 and abs (y-ly)<20:
                        label = ltext
                        current_labels.append((x,y,label))
                        break
        for (x, y, label) in current_labels:
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 244, 0), 2)
            
        frame_count +=1
        if (frame_count>325):
            frame_count=0
        
        cv2.imshow("Face Detection", frame)

        
        if cv2.waitKey(1) & 0xFF == ord('q'):  
            break
    camera.release()
    cv2.destroyAllWindows()
      
capture_loop()