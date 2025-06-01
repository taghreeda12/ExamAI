import cv2
import threading
import time
import numpy as np
import sounddevice as sd
import os
from datetime import datetime
from functionKM import start_listeners
import pandas as pd
df = pd.read_csv('mazeComparison1.csv') 
print(df.head())

events = []

def add_event(event):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    events.append(f"[{now}] {event}")

def write_events():
    while True:
        if events:
            with open("event_log.txt", "a", encoding="utf-8") as file:
                file.write("\n".join(events) + "\n")
            events.clear()
        time.sleep(5)

def check_audio():
    audio = sd.rec(int(44100), samplerate=44100, channels=1, dtype='float64')
    sd.wait()
    return np.linalg.norm(audio) * 10 > 1.0

def play_alert():
    os.system("say 'Alert'")

threading.Thread(target=start_listeners, daemon=True).start()
threading.Thread(target=write_events, daemon=True).start()

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

cam = cv2.VideoCapture(0)
cam.set(3, 320)
cam.set(4, 240)

if not cam.isOpened():
    exit()

video = cv2.VideoWriter(f"recording_{int(time.time())}.avi", cv2.VideoWriter_fourcc(*'XVID'), 20.0, (320, 240))

last_snap = time.time()
last_audio = time.time()
audio_flag = False

while True:
    ret, frame = cam.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    eyes_all = 0
    looking_out = 0

    for (x, y, w, h) in faces:
        add_event("Face detected")
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 10)
        eyes_all += len(eyes)
        if len(eyes) < 2:
            looking_out += 1
        for (ex, ey, ew, eh) in eyes:
            add_event("Eye detected")
            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

    if time.time() - last_audio > 1:
        audio_flag = check_audio()
        if audio_flag:
            add_event("Sound detected")
        last_audio = time.time()

    if audio_flag or looking_out > 0:
        play_alert()

    cv2.putText(frame, f"Faces: {len(faces)} | Eyes: {eyes_all} | Audio: {'Yes' if audio_flag else 'No'} | Away: {looking_out}",
                (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    video.write(frame)
    cv2.imshow("Monitor", frame)

    if len(faces) > 0 and (time.time() - last_snap > 10):
        name = f"snapshot_{int(time.time())}.jpg"
        cv2.imwrite(name, frame)
        add_event(f"Snapshot saved: {name}")
        last_snap = time.time()

    if cv2.waitKey(1) in [27, ord('q')]:
        break

cam.release()
video.release()
cv2.destroyAllWindows()
