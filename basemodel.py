# =============================================================================
# basemodel.py - Monitoring System
# =============================================================================

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
stop_flag = threading.Event()  # Add stop flag

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
                print(f"✅ تم حفظ الصورة باسم {filename}")
                log_event(f"Snapshot taken: {filename}")
            else:
                print("❌ لم يتم التقاط صورة")
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
        
        # Keep listeners alive
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
        if key in [27, ord('q')]:  # ESC or 'q'
            stop_flag.set()
            break

    cam.release()
    video.release()
    cv2.destroyAllWindows()

def run_the_back():
    logging.info("Starting monitoring system...")
    
    # Start all threads
    threads = []
    
    try:
        # Start event writer
        event_thread = threading.Thread(target=write_events)
        event_thread.start()
        threads.append(event_thread)
        
        # Start input listeners
        listener_thread = threading.Thread(target=start_listeners)
        listener_thread.start()
        threads.append(listener_thread)
        
        # Start periodic snapshots
        snapshot_thread = threading.Thread(target=take_snapshot_periodically)
        snapshot_thread.start()
        threads.append(snapshot_thread)
        
        # Start video monitoring (this will be the main loop)
        video_loop()
    except Exception as e:
        logging.error(f"Error in monitoring system: {e}")
        stop_flag.set()
    finally:
        # Ensure all threads are stopped
        stop_flag.set()
        for thread in threads:
            thread.join(timeout=5)
        logging.info("Monitoring system stopped.")

if __name__ == "__main__":
    run_the_back()

# import cv2
# import threading
# import time
# import numpy as np
# import sounddevice as sd
# import os
# from datetime import datetime
# import pyautogui
# import dlib
# from pynput import keyboard, mouse
# from scipy.spatial import distance
# import pandas as pd

# # Load CSV data
# try:
#     df = pd.read_csv('mazeComparison1.csv') 
#     print(df.head())
# except FileNotFoundError:
#     print("CSV file not found, continuing without it...")

# events = []
# stop_flag = threading.Event()  # Add stop flag

# def add_event(event):
#     now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     events.append(f"[{now}] {event}")

# def write_events():
#     while not stop_flag.is_set():
#         if events:
#             with open("event_log.txt", "a", encoding="utf-8") as file:
#                 file.write("\n".join(events) + "\n")
#             events.clear()
#         time.sleep(5)

# def check_audio():
#     try:
#         audio = sd.rec(int(44100), samplerate=44100, channels=1, dtype='float64')
#         sd.wait()
#         return np.linalg.norm(audio) * 10 > 1.0
#     except:
#         return False

# def play_alert():
#     try:
#         os.system("say 'Alert'")
#     except:
#         print("Alert!")

# def log_event(text):
#     with open("activity_log.txt", "a", encoding="utf-8") as file:
#         timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#         file.write(f"[{timestamp}] {text}\n")

# def on_key_press(key):
#     try:
#         log_event(f"Key: {key.char}")
#     except AttributeError:
#         log_event(f"Special Key: {key}")
#     if key == keyboard.Key.esc:
#         stop_flag.set()
#         return False

# def on_mouse_move(x, y):
#     log_event(f"Mouse moved to ({x}, {y})")

# def on_mouse_click(x, y, button, pressed):
#     action = "Pressed" if pressed else "Released"
#     log_event(f"Mouse {action} {button} at ({x}, {y})")

# def on_mouse_scroll(x, y, dx, dy):
#     log_event(f"Mouse scroll at ({x}, {y}) by ({dx}, {dy})")

# def take_snapshot_periodically():
#     while not stop_flag.is_set():
#         try:
#             video_capture = cv2.VideoCapture(0)
#             ret, frame = video_capture.read()
#             video_capture.release()

#             if ret:
#                 timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
#                 filename = f"snapshot_{timestamp}.jpg"
#                 cv2.imwrite(filename, frame)
#                 print(f"✅ تم حفظ الصورة باسم {filename}")
#                 log_event(f"Snapshot taken: {filename}")
#             else:
#                 print("❌ لم يتم التقاط صورة")
#                 log_event("Snapshot failed")
#         except Exception as e:
#             print(f"Snapshot error: {e}")
#             log_event(f"Snapshot error: {e}")

#         time.sleep(20)

# def start_listeners():
#     try:
#         kb_listener = keyboard.Listener(on_press=on_key_press)
#         ms_listener = mouse.Listener(
#             on_move=on_mouse_move,
#             on_click=on_mouse_click,
#             on_scroll=on_mouse_scroll
#         )
#         kb_listener.start()
#         ms_listener.start()
#         print("Input listeners started successfully")
        
#         # Keep listeners alive
#         while not stop_flag.is_set():
#             time.sleep(1)
            
#     except Exception as e:
#         print(f"Listener error: {e}")
#         log_event(f"Listener error: {e}")

# def video_loop():
#     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
#     eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

#     cam = cv2.VideoCapture(0)
#     cam.set(3, 320)
#     cam.set(4, 240)

#     if not cam.isOpened():
#         print("Cannot open camera")
#         return

#     video = cv2.VideoWriter(f"recording_{int(time.time())}.avi", cv2.VideoWriter_fourcc(*'XVID'), 20.0, (320, 240))
#     audio_flag = False

#     print("Video monitoring started. Press 'q' or ESC to quit.")
    
#     while not stop_flag.is_set():
#         ret, frame = cam.read()
#         if not ret:
#             break

#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         faces = face_cascade.detectMultiScale(gray, 1.3, 5)
#         eyes_all = 0
#         looking_out = 0

#         for (x, y, w, h) in faces:
#             add_event("Face detected")
#             cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
#             roi_gray = gray[y:y + h, x:x + w]
#             roi_color = frame[y:y + h, x:x + w]
#             eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 10)
#             eyes_all += len(eyes)
#             if len(eyes) < 2:
#                 looking_out += 1
#             for (ex, ey, ew, eh) in eyes:
#                 add_event("Eye detected")
#                 cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

#         cv2.putText(frame, f"Faces: {len(faces)} | Eyes: {eyes_all} | Audio: {'Yes' if audio_flag else 'No'} | Away: {looking_out}",
#                     (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

#         video.write(frame)
#         cv2.imshow("Monitor", frame)

#         key = cv2.waitKey(1) & 0xFF
#         if key in [27, ord('q')]:  # ESC or 'q'
#             stop_flag.set()
#             break

#     cam.release()
#     video.release()
#     cv2.destroyAllWindows()

# def run_the_back():
#     logging.info("Starting monitoring system...")
    
#     # Start all threads
#     threads = []
    
#     try:
#         # Start event writer
#         event_thread = threading.Thread(target=write_events)
#         event_thread.start()
#         threads.append(event_thread)
        
#         # Start input listeners
#         listener_thread = threading.Thread(target=start_listeners)
#         listener_thread.start()
#         threads.append(listener_thread)
        
#         # Start periodic snapshots
#         snapshot_thread = threading.Thread(target=take_snapshot_periodically)
#         snapshot_thread.start()
#         threads.append(snapshot_thread)
        
#         # Start video monitoring (this will be the main loop)
#         video_loop()
#     except Exception as e:
#         logging.error(f"Error in monitoring system: {e}")
#         stop_flag.set()
#     finally:
#         # Ensure all threads are stopped
#         stop_flag.set()
#         for thread in threads:
#             thread.join(timeout=5)
#         logging.info("Monitoring system stopped.")

# if __name__ == "__main__":
#     run_the_back()


# import cv2
# import threading
# import time
# import numpy as np
# import sounddevice as sd
# import os
# from datetime import datetime
# import pyautogui
# import cv2
# import dlib
# import threading
# import time
# from pynput import keyboard, mouse
# import numpy as np
# from scipy.spatial import distance

# from functionKM import start_listeners
# import pandas as pd
# df = pd.read_csv('mazeComparison1.csv') 
# print(df.head())

# events = []

# def add_event(event):
#     now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     events.append(f"[{now}] {event}")

# def write_events():
#     while True:
#         if events:
#             with open("event_log.txt", "a", encoding="utf-8") as file:
#                 file.write("\n".join(events) + "\n")
#             events.clear()
#         time.sleep(5)

# def check_audio():
#     audio = sd.rec(int(44100), samplerate=44100, channels=1, dtype='float64')
#     sd.wait()
#     return np.linalg.norm(audio) * 10 > 1.0

# def play_alert():
#     os.system("say 'Alert'")

# # وظيفة للتسجيل في ملف
# def log_event(text):
#     with open("activity_log.txt", "a", encoding="utf-8") as file:
#         timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#         file.write(f"[{timestamp}] {text}\n")

# # التعامل مع ضغط المفاتيح
# def on_key_press(key):
#     try:
#         log_event(f"Key: {key.char}")
#     except AttributeError:
#         log_event(f"Special Key: {key}")
#     if key == keyboard.Key.esc:
#         #stop_flag.set()
#         return False

# def on_mouse_move(x, y):
#     log_event(f"Mouse moved to ({x}, {y})")

# def on_mouse_click(x, y, button, pressed):
#     action = "Pressed" if pressed else "Released"
#     log_event(f"Mouse {action} {button} at ({x}, {y})")

# def on_mouse_scroll(x, y, dx, dy):
#     log_event(f"Mouse scroll at ({x}, {y}) by ({dx}, {dy})")

# def take_snapshot_periodically():
#     while True:
#         video_capture = cv2.VideoCapture(0)  # Use the correct camera index
#         ret, frame = video_capture.read()
#         video_capture.release()

#         if ret:
#             timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
#             filename = f"snapshot_{timestamp}.jpg"
#             cv2.imwrite(filename, frame)
#             print(f"✅ تم حفظ الصورة باسم {filename}")
#             log_event(f"Snapshot taken: {filename}")
#         else:
#             print("❌ لم يتم التقاط صورة")
#             log_event("Snapshot failed")

#         time.sleep(20)  # Wait for 20 seconds

# threading.Thread(target=start_listeners, daemon=True).start()
# threading.Thread(target=write_events, daemon=True).start()

# face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
# eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

# cam = cv2.VideoCapture(0)
# cam.set(3, 320)
# cam.set(4, 240)

# if not cam.isOpened():
#     exit()

# video = cv2.VideoWriter(f"recording_{int(time.time())}.avi", cv2.VideoWriter_fourcc(*'XVID'), 20.0, (320, 240))

# last_snap = time.time()
# last_audio = time.time()
# audio_flag = False

# def video_loop():
#     while True:
#         ret, frame = cam.read()
#         if not ret:
#             break

#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         faces = face_cascade.detectMultiScale(gray, 1.3, 5)
#         eyes_all = 0
#         looking_out = 0

#         for (x, y, w, h) in faces:
#             add_event("Face detected")
#             cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
#             roi_gray = gray[y:y + h, x:x + w]
#             roi_color = frame[y:y + h, x:x + w]
#             eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 10)
#             eyes_all += len(eyes)
#             if len(eyes) < 2:
#                 looking_out += 1
#             for (ex, ey, ew, eh) in eyes:
#                 add_event("Eye detected")
#                 cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)


#         cv2.putText(frame, f"Faces: {len(faces)} | Eyes: {eyes_all} | Audio: {'Yes' if audio_flag else 'No'} | Away: {looking_out}",
#                     (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

#         video.write(frame)
#         cv2.imshow("Monitor", frame)

#         # if len(faces) > 0 and (time.time() - last_snap > 10):
#         #     name = f"snapshot_{int(time.time())}.jpg"
#         #     cv2.imwrite(name, frame)
#         #     add_event(f"Snapshot saved: {name}")
#         #     last_snap = time.time()

#         if cv2.waitKey(1) in [27, ord('q')]:
#             break

#     cam.release()
#     video.release()
#     cv2.destroyAllWindows()


# def start_listeners():
#     kb_listener = keyboard.Listener(on_press=on_key_press)
#     ms_listener = mouse.Listener(
#         on_move=on_mouse_move,
#         on_click=on_mouse_click,
#         on_scroll=on_mouse_scroll
#     )
#     kb_listener.start()
#     ms_listener.start()


# def run():
#     threading.Thread(target=video_loop, daemon=True).start()
#     threading.Thread(target=start_listeners, daemon=True).start()
#     threading.Thread(target=take_snapshot_periodically, daemon=True).start()
#     # start_listeners()
# if __name__ == "__main__":
#     run()
    # video_loop()
    # start_listeners()



# import cv2
# import threading
# import time
# import numpy as np
# import sounddevice as sd
# import os
# from datetime import datetime
# from functionKM import start_listeners
# import pandas as pd
# df = pd.read_csv('mazeComparison1.csv') 
# print(df.head())

# events = []

# def add_event(event):
#     now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     events.append(f"[{now}] {event}")

# def write_events():
#     while True:
#         if events:
#             with open("event_log.txt", "a", encoding="utf-8") as file:
#                 file.write("\n".join(events) + "\n")
#             events.clear()
#         time.sleep(5)

# def check_audio():
#     audio = sd.rec(int(44100), samplerate=44100, channels=1, dtype='float64')
#     sd.wait()
#     return np.linalg.norm(audio) * 10 > 1.0

# def play_alert():
#     os.system("say 'Alert'")

# threading.Thread(target=start_listeners, daemon=True).start()
# threading.Thread(target=write_events, daemon=True).start()

# face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
# eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

# cam = cv2.VideoCapture(0)
# cam.set(3, 320)
# cam.set(4, 240)

# if not cam.isOpened():
#     exit()

# video = cv2.VideoWriter(f"recording_{int(time.time())}.avi", cv2.VideoWriter_fourcc(*'XVID'), 20.0, (320, 240))

# last_snap = time.time()
# last_audio = time.time()
# audio_flag = False

# while True:
#     ret, frame = cam.read()
#     if not ret:
#         break

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     faces = face_cascade.detectMultiScale(gray, 1.3, 5)
#     eyes_all = 0
#     looking_out = 0

#     for (x, y, w, h) in faces:
#         add_event("Face detected")
#         cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
#         roi_gray = gray[y:y + h, x:x + w]
#         roi_color = frame[y:y + h, x:x + w]
#         eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 10)
#         eyes_all += len(eyes)
#         if len(eyes) < 2:
#             looking_out += 1
#         for (ex, ey, ew, eh) in eyes:
#             add_event("Eye detected")
#             cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)


#     cv2.putText(frame, f"Faces: {len(faces)} | Eyes: {eyes_all} | Audio: {'Yes' if audio_flag else 'No'} | Away: {looking_out}",
#                 (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

#     video.write(frame)
#     cv2.imshow("Monitor", frame)

#     if len(faces) > 0 and (time.time() - last_snap > 10):
#         name = f"snapshot_{int(time.time())}.jpg"
#         cv2.imwrite(name, frame)
#         add_event(f"Snapshot saved: {name}")
#         last_snap = time.time()

#     if cv2.waitKey(1) in [27, ord('q')]:
#         break

# cam.release()
# video.release()
# cv2.destroyAllWindows()

#     # if time.time() - last_audio > 1:
#     #     audio_flag = check_audio()
#     #     if audio_flag:
#     #         add_event("Sound detected")
#     #     last_audio = time.time()

#     # if audio_flag or looking_out > 0:
#     #     play_alert()\


# # import cv2
# # import dlib
# # import threading
# # import time
# # from pynput import keyboard, mouse
# # import numpy as np
# # from scipy.spatial import distance

# # detector = dlib.get_frontal_face_detector()
# # predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
# # #predictor = dlib.shape_predictor('/Users/taghridamohamed/TagProP.py/shape_predictor_68_face_landmarks.dat')

# # def eye_aspect_ratio(eye):
# #     A = distance.euclidean(eye[1], eye[5])
# #     B = distance.euclidean(eye[2], eye[4])
# #     C = distance.euclidean(eye[0], eye[3])
# #     return (A + B) / (2.0 * C)

# # # إعداد الكاميرا
# # cap = cv2.VideoCapture(0)

# # # معايير التحذير
# # EAR_THRESHOLD = 0.25
# # FRAME_COUNT_THRESHOLD = 20
# # frame_count = 0
# # warned = False

# # # وظيفة للكشف عن الوجوه باستخدام dlib
# # def detect_faces_with_dlib(frame):
# #     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# #     faces = detector(gray)
# #     return faces

# # # وظيفة للتسجيل في ملف
# # def log_event(text):
# #     with open("activity_log.txt", "a", encoding="utf-8") as file:
# #         timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
# #         file.write(f"[{timestamp}] {text}\n")

# # # التعامل مع ضغط المفاتيح
# # def on_key_press(key):
# #     try:
# #         log_event(f"Key: {key.char}")
# #     except AttributeError:
# #         log_event(f"Special Key: {key}")
# #     if key == keyboard.Key.esc:
# #         #stop_flag.set()
# #         return False

# # def on_mouse_move(x, y):
# #     log_event(f"Mouse moved to ({x}, {y})")

# # def on_mouse_click(x, y, button, pressed):
# #     action = "Pressed" if pressed else "Released"
# #     log_event(f"Mouse {action} {button} at ({x}, {y})")

# # def on_mouse_scroll(x, y, dx, dy):
# #     log_event(f"Mouse scroll at ({x}, {y}) by ({dx}, {dy})")

# # # def take_snapshot():
# # #     video_capture = cv2.VideoCapture(0)  # استخدم 0 أو 1 حسب الكاميرا المتوفرة

# # #     ret, frame = video_capture.read()
# # #     video_capture.release()

# # #     if ret:
# # #         cv2.imwrite("snapshot.jpg", frame)
# # #         print("✅ تم حفظ الصورة باسم snapshot.jpg")
# # #     else:
# # #         print("❌ لم يتم التقاط صورة")

# # def take_snapshot_periodically():
# #     while True:
# #         video_capture = cv2.VideoCapture(0)  # Use the correct camera index
# #         ret, frame = video_capture.read()
# #         video_capture.release()

# #         if ret:
# #             timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
# #             filename = f"snapshot_{timestamp}.jpg"
# #             cv2.imwrite(filename, frame)
# #             print(f"✅ تم حفظ الصورة باسم {filename}")
# #             log_event(f"Snapshot taken: {filename}")
# #         else:
# #             print("❌ لم يتم التقاط صورة")
# #             log_event("Snapshot failed")

# #         time.sleep(20)  # Wait for 20 seconds

# # def video_loop():
# #     global frame_count, warned
# #     cap = cv2.VideoCapture(0)
# #     while True:
# #         ret, frame = cap.read()
# #         if not ret:
# #             break

# #         faces = detect_faces_with_dlib(frame)

# #         for face in faces:
# #             landmarks = predictor(frame, face)
# #             left_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]
# #             right_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]

# #             left_ear = eye_aspect_ratio(left_eye)
# #             right_ear = eye_aspect_ratio(right_eye)

# #             ear = (left_ear + right_ear) / 2.0

# #             if ear < EAR_THRESHOLD:
# #                 frame_count += 1
# #                 if frame_count >= FRAME_COUNT_THRESHOLD and not warned:
# #                     cv2.putText(frame, "تحذير: العين مغلقة لفترة طويلة!", (50, 50),
# #                                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
# #                     warned = True
# #             else:
# #                 frame_count = 0
# #                 warned = False

# #             x, y, w, h = (face.left(), face.top(), face.width(), face.height())
# #             cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

# #         cv2.imshow("Face Detection", frame)

# #         if cv2.waitKey(1) & 0xFF == ord('q'):
# #             break

# #     cap.release()
# #     cv2.destroyAllWindows()

# # def start_listeners():
# #     kb_listener = keyboard.Listener(on_press=on_key_press)
# #     ms_listener = mouse.Listener(
# #         on_move=on_mouse_move,
# #         on_click=on_mouse_click,
# #         on_scroll=on_mouse_scroll
# #     )
# #     kb_listener.start()
# #     ms_listener.start()

# # def run():
# #     threading.Thread(target=video_loop, daemon=True).start()
# #     threading.Thread(target=take_snapshot_periodically, daemon=True).start()
# #     start_listeners()

# # if __name__ == "__main__":
# #     run()