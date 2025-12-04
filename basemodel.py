import cv2
import threading
import time
import numpy as np
import sounddevice as sd
import os
from datetime import datetime
import pyautogui
import dlib
from pynput import keyboard, mouse
from scipy.spatial import distance
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load CSV data
try:
    df = pd.read_csv('mazeComparison1.csv') 
    print(df.head())
except FileNotFoundError:
    print("CSV file not found, continuing without it...")

events = []
stop_flag = threading.Event()  # Stop flag for threads

def add_event(event):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    events.append(f"[{now}] {event}")

def write_events():
    while not stop_flag.is_set():
        if events:
            with open("event_log.txt", "a", encoding="utf-8") as file:
                file.write("\n".join(events) + "\n")
            events.clear()
        time.sleep(5)

def check_audio():
    try:
        audio = sd.rec(int(44100), samplerate=44100, channels=1, dtype='float64')
        sd.wait()
        return np.linalg.norm(audio) * 10 > 1.0
    except:
        return False

def play_alert():
    try:
        os.system("say 'Alert'")
    except:
        print("Alert!")

def log_event(text):
    with open("activity_log.txt", "a", encoding="utf-8") as file:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        file.write(f"[{timestamp}] {text}\n")

def on_key_press(key):
    try:
        log_event(f"Key: {key.char}")
    except AttributeError:
        log_event(f"Special Key: {key}")
    if key == keyboard.Key.esc:
        stop_flag.set()
        return False

def on_mouse_move(x, y):
    log_event(f"Mouse moved to ({x}, {y})")

def on_mouse_click(x, y, button, pressed):
    action = "Pressed" if pressed else "Released"
    log_event(f"Mouse {action} {button} at ({x}, {y})")

def on_mouse_scroll(x, y, dx, dy):
    log_event(f"Mouse scroll at ({x}, {y}) by ({dx}, {dy})")

def take_snapshot_periodically():
    while not stop_flag.is_set():
        try:
            video_capture = cv2.VideoCapture(0)
            ret, frame = video_capture.read()
            video_capture.release()

            if ret:
                timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
                filename = f"snapshot_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"✅ Snapshot saved as {filename}")
                log_event(f"Snapshot taken: {filename}")
            else:
                print("❌ Failed to take snapshot")
                log_event("Snapshot failed")
        except Exception as e:
            print(f"Snapshot error: {e}")
            log_event(f"Snapshot error: {e}")

        time.sleep(20)

def start_listeners():
    try:
        kb_listener = keyboard.Listener(on_press=on_key_press)
        ms_listener = mouse.Listener(
            on_move=on_mouse_move,
            on_click=on_mouse_click,
            on_scroll=on_mouse_scroll
        )
        kb_listener.start()
        ms_listener.start()
        print("Input listeners started successfully")
        
        while not stop_flag.is_set():
            time.sleep(1)
            
    except Exception as e:
        print(f"Listener error: {e}")
        log_event(f"Listener error: {e}")

def video_loop():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

    cam = cv2.VideoCapture(0)
    cam.set(3, 320)
    cam.set(4, 240)

    if not cam.isOpened():
        print("Cannot open camera")
        return

    video = cv2.VideoWriter(f"recording_{int(time.time())}.avi", cv2.VideoWriter_fourcc(*'XVID'), 20.0, (320, 240))
    audio_flag = False

    print("Video monitoring started. Press 'q' or ESC to quit.")
    
    while not stop_flag.is_set():
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

        cv2.putText(frame, f"Faces: {len(faces)} | Eyes: {eyes_all} | Audio: {'Yes' if audio_flag else 'No'} | Away: {looking_out}",
                    (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        video.write(frame)
        cv2.imshow("Monitor", frame)

        key = cv2.waitKey(1) & 0xFF
        if key in [27, ord('q')]:
            stop_flag.set()
            break

    cam.release()
    video.release()
    cv2.destroyAllWindows()

def run_the_back():
    logging.info("Starting monitoring system...")
    
    threads = []
    
    try:
        event_thread = threading.Thread(target=write_events)
        event_thread.start()
        threads.append(event_thread)
        
        listener_thread = threading.Thread(target=start_listeners)
        listener_thread.start()
        threads.append(listener_thread)
        
        snapshot_thread = threading.Thread(target=take_snapshot_periodically)
        snapshot_thread.start()
        threads.append(snapshot_thread)
        
        video_loop()
    except Exception as e:
        logging.error(f"Error in monitoring system: {e}")
        stop_flag.set()
    finally:
        stop_flag.set()
        for thread in threads:
            thread.join(timeout=5)
        logging.info("Monitoring system stopped.")

if __name__ == "__main__":
    run_the_back()
