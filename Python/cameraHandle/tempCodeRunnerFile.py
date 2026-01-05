## COMPONENT TEST FILE 
# 30/04 10:16pm
# read laptop's front camera

# Problem with the model: when the background has heavy texture, 
# like wooden walls or many objects behind, 
# the model tends to classify samples with tied-back hair as male. => retrain model "gender_retrain"
# in this file, the old model: gender_oval_blur.tflite is still used

# if the values appear to be more than 0.9 in a batch time, the average_gender result will be set to 1.2
# good result :>> (test with my face: female - 2x)

import cv2
import os
import sys
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.merge01_gender import gender_predict
from utils.merge01_age import age_predict, find_most_common_age_group
    

def capture_loop():  
    face_cascade = cv2.CascadeClassifier('assets/haarcascade_frontalface_alt.xml')
    camera = cv2.VideoCapture(0)
    count = 0
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
    ages = []
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
            if frame_count % process_every_n_frames ==0:
                # handle gender
                full_frame = frame.copy()
                gender = gender_predict(full_frame, x, y, w, h)
                
                face_img = frame[y:y+h, x:x+w].copy()
                age = age_predict(face_img)
                ages.append(age)
                
                # cv2.rectangle(frame, (x,y),(x+w,y+h),(255,255,0),3)
                if gender>0.9: 
                    count +=1
                gender_average.append(gender)
                if len(gender_average) == gender_el_count:
                    avg_gender = sum(gender_average)/gender_el_count
                    if avg_gender < 0.5:
                        if count>=3:
                            avg_gender=1.2
                    genderstr = str(avg_gender)
                    ######
                    count = 0
                    current_labels.append((x,y,genderstr))
                    gender_average = []
                    
                    most_common_age_group = find_most_common_age_group(ages)
                    agestr = str(most_common_age_group)
                    ######
                    print(f"HEHEHE {genderstr} {agestr}")
                    ages = []
                    
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