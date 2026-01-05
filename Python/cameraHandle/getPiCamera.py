from picamera2 import Picamera2

import time
import cv2
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# sys.path.append(os.path.abspath("../G&A_DETECTION/"))
# from utils.tf_model_handle_copy import lite_predict_ga   
from utils.tf_pi import lite_predict_ga   

def capture_loop():
    face_cascade = cv2.CascadeClassifier('assets/haarcascade_frontalface_alt.xml')
    
    frame_count = 0
    process_every_n_frames =30
    
    camera = Picamera2()
    config = camera.create_preview_configuration(main={"format":"RGB888", "size":(700,600)})
    camera.configure(config)
    camera.start()
    time.sleep(1)

    face_labels = []
    while (True):
        frame = camera.capture_array()
        frame = cv2.flip(frame,1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=7, minSize=(30, 30))
        current_labels = []
        for (x,y,w,h) in faces:
            cv2.rectangle(frame, (x,y),(x+w,y+h),(255,255,0),3)
            
            if frame_count % process_every_n_frames ==0:
                face_img = frame[y:y+h, x:x+w].copy()
                age, gender = lite_predict_ga(face_img)
                # print(a)
                
                label = f"{gender}, {age}"
                current_labels.append((x,y,label))
            else:
                for (lx, ly, ltext) in face_labels:
                    if abs(x-lx)<20 and abs(y-ly)<20:
                        label = ltext
                        current_labels.append((x,y,label))
                        break
        for (x,y,label) in current_labels:
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,0.7, (0, 255, 0), 2)
            
        if frame_count % process_every_n_frames == 0:
            face_labels = current_labels.copy()
        frame_count +=1 
        if (frame_count>325):
            frame_count=0
        
        # label = f"{gender}, {age}"        
        
        cv2.imshow("camera",frame)
        if cv2.waitKey(1)==ord("q"):
            break
    cv2.destroyAllWindows()
    camera.stop()

capture_loop()
