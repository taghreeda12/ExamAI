import cv2
import dlib
import threading
import time
from pynput import keyboard, mouse
import numpy as np
from scipy.spatial import distance

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
#predictor = dlib.shape_predictor('/Users/taghridamohamed/TagProP.py/shape_predictor_68_face_landmarks.dat')

def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

# إعداد الكاميرا
cap = cv2.VideoCapture(0)

# معايير التحذير
EAR_THRESHOLD = 0.25
FRAME_COUNT_THRESHOLD = 20
frame_count = 0
warned = False

# وظيفة للكشف عن الوجوه باستخدام dlib
def detect_faces_with_dlib(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    return faces

# وظيفة للتسجيل في ملف
def log_event(text):
    with open("activity_log.txt", "a", encoding="utf-8") as file:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        file.write(f"[{timestamp}] {text}\n")

# التعامل مع ضغط المفاتيح
def on_key_press(key):
    try:
        log_event(f"Key: {key.char}")
    except AttributeError:
        log_event(f"Special Key: {key}")
    if key == keyboard.Key.esc:
        #stop_flag.set()
        return False

def on_mouse_move(x, y):
    log_event(f"Mouse moved to ({x}, {y})")

def on_mouse_click(x, y, button, pressed):
    action = "Pressed" if pressed else "Released"
    log_event(f"Mouse {action} {button} at ({x}, {y})")

def on_mouse_scroll(x, y, dx, dy):
    log_event(f"Mouse scroll at ({x}, {y}) by ({dx}, {dy})")

def video_loop():
    global frame_count, warned
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        faces = detect_faces_with_dlib(frame)

        for face in faces:
            landmarks = predictor(frame, face)
            left_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]
            right_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]

            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)

            ear = (left_ear + right_ear) / 2.0

            if ear < EAR_THRESHOLD:
                frame_count += 1
                if frame_count >= FRAME_COUNT_THRESHOLD and not warned:
                    cv2.putText(frame, "تحذير: العين مغلقة لفترة طويلة!", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    warned = True
            else:
                frame_count = 0
                warned = False

            x, y, w, h = (face.left(), face.top(), face.width(), face.height())
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        cv2.imshow("Face Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def start_listeners():
    kb_listener = keyboard.Listener(on_press=on_key_press)
    ms_listener = mouse.Listener(
        on_move=on_mouse_move,
        on_click=on_mouse_click,
        on_scroll=on_mouse_scroll
    )
    kb_listener.start()
    ms_listener.start()

def run():
    threading.Thread(target=video_loop, daemon=True).start()
    start_listeners()

if __name__ == "__main__":
    run()

