#see from above: female => male
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import cv2
import threading
import time
import numpy as np 
from utils.merge01_age import age_predict, find_most_common_age_group, load_age_model
from utils.merge01_gender import gender_predict, load_gender_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_gender_model()
    load_age_model()
    yield
    
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],  # Only accept request from this address
    allow_credentials=True,
    allow_methods=["*"],  # accept all methods
    allow_headers=["*"],  # accept all headers
)

lock = threading.Lock()
face_cascade = cv2.CascadeClassifier('assets/haarcascade_frontalface_alt.xml')
current_frame = None

def camera_loop():
    global current_frame
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        with lock:
            current_frame = cv2.flip(frame, 1)
        # time.sleep(0.02)

@app.get("/analyze")       
def analyze_face():
    print('ANALYZE START')
    frames_per_process = 5
    process_num = 15
    face_cascade = cv2.CascadeClassifier('assets/haarcascade_frontalface_alt.xml')

    frame_count = 0
    process_no = 0
    f_count = 0
    genders = []
    ages = []
    
    while process_no < process_num:
        with lock:
            if current_frame is None:
                time.sleep(0.05) #why
                continue
            full_frame = current_frame.copy()
            
        frame_count +=1
        if frame_count % frames_per_process != 0:
            continue
        gray = cv2.cvtColor(full_frame, cv2.COLOR_BGR2GRAY)
        
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=7, minSize=(30, 30))
        if len(faces) == 0: continue
        
        for (x, y, w, h) in faces:
            face_img = full_frame[y:y+h, x:x+w].copy()
            # cv2.imwrite(f"debug/face_{process_no}.jpg", face_img)
            age = age_predict(face_img)
            
            gender = gender_predict(full_frame, x, y, w, h)
            if gender<0.3: age = age + 5
            print(gender)
            genders.append(gender)
            ages.append(age)
            
            if gender > 0.98:
                f_count += 1

            process_no += 1
            break
             
    if len(genders) == process_num:
        gender_average = sum(float(g) for g in genders)/process_num
        if gender_average < 0.5:
            if f_count >=3:
                gender_average = 1.2
        age_group = find_most_common_age_group(ages)
        print(f"{gender_average} {age_group}")
        return {"age": age_group, "gender": gender_average}
    else: 
        return {"error": "an error occurred in analyze function."}        
        
threading.Thread(target=camera_loop, daemon=True).start()         