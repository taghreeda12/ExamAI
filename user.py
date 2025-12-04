import tkinter as tk
from tkinter import ttk, messagebox
import threading
from basemodel import run_the_back
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

monitoring_thread = None

def start_quiz_window(title):
    global monitoring_thread

    # Start monitoring system if not running
    if monitoring_thread is None or not monitoring_thread.is_alive():
        logging.info("Starting monitoring system...")
        monitoring_thread = threading.Thread(target=run_the_back, daemon=True)
        monitoring_thread.start()
        logging.info("Monitoring system started.")
    else:
        logging.info("Monitoring system already running.")

    quiz_window = tk.Toplevel()
    quiz_window.title(f"Quiz - {title}")
    quiz_window.geometry("500x400")
    quiz_window.resizable(False, False)

    # Header
    header_frame = tk.Frame(quiz_window, bg="lightblue")
    header_frame.pack(fill="x")
    tk.Label(header_frame, text=title, font=("Arial", 16, "bold"), bg="lightblue").pack(pady=10)

    # Warning section
    warning_frame = tk.Frame(quiz_window, bg="#ffeb3b", relief="solid", bd=2)
    warning_frame.pack(fill="x", padx=10, pady=10)
    tk.Label(warning_frame, text="Monitoring system is active during the quiz", 
             bg="#ffeb3b", font=("Arial", 10, "bold"), fg="red").pack(pady=5)
    tk.Label(warning_frame, text="All activities and movements will be recorded", 
             bg="#ffeb3b", font=("Arial", 9)).pack(pady=2)

    # Question section
    question_frame = tk.LabelFrame(quiz_window, text="Question 1", font=("Arial", 12, "bold"))
    question_frame.pack(fill="both", expand=True, padx=20, pady=10)
    tk.Label(question_frame, text="What is the capital of Egypt?", font=("Arial", 12), wraplength=400).pack(pady=15)

    answer_var = tk.StringVar()
    options = [
        ("Cairo", "Cairo"),
        ("Alexandria", "Alexandria"),
        ("Giza", "Giza"),
        ("Khartoum", "Khartoum")
    ]
    for text, value in options:
        ttk.Radiobutton(question_frame, text=text, variable=answer_var, value=value).pack(anchor="w", padx=40, pady=3)

    # Timer
    timer_frame = tk.Frame(quiz_window)
    timer_frame.pack(pady=5)
    tk.Label(timer_frame, text="Time remaining:", font=("Arial", 10)).pack(side="left")
    timer_label = tk.Label(timer_frame, text="05:00", font=("Arial", 10, "bold"), fg="green")
    timer_label.pack(side="left", padx=5)

    remaining_time = 300  # 5 minutes

    def update_timer():
        nonlocal remaining_time
        if remaining_time > 0:
            mins = remaining_time // 60
            secs = remaining_time % 60
            timer_label.config(text=f"{mins:02d}:{secs:02d}")
            if remaining_time <= 60:
                timer_label.config(fg="red")
            remaining_time -= 1
            quiz_window.after(1000, update_timer)
        else:
            timer_label.config(text="Time's up!", fg="red")
            submit_quiz()

    def submit_quiz():
        if not answer_var.get():
            messagebox.showwarning("Warning", "You must select an answer before submitting!")
            return
        if answer_var.get() == "Cairo":
            messagebox.showinfo("Result", "Correct answer! Score: 10/10\nQuiz submitted successfully.")
        else:
            messagebox.showinfo("Result", f"Wrong answer! Correct: Cairo\nYour answer: {answer_var.get()}\nScore: 0/10")
        quiz_window.destroy()

    # Buttons
    button_frame = tk.Frame(quiz_window)
    button_frame.pack(pady=15)
    ttk.Button(button_frame, text="Submit Quiz", command=submit_quiz).pack(side="left", padx=10)
    ttk.Button(button_frame, text="Cancel", command=quiz_window.destroy).pack(side="left", padx=10)

    update_timer()


def start_quiz(title):
    response = messagebox.askyesno("Start Quiz", 
                                   f"Do you want to start the quiz: {title}?\n\n"
                                   "Note:\n"
                                   "- Monitoring system will be active automatically\n"
                                   "- Camera and audio will be recorded\n"
                                   "- Mouse and keyboard movements will be tracked\n"
                                   "- Time limit: 5 minutes\n\n"
                                   "Do you want to continue?")
    if response:
        start_quiz_window(title)


# Main Window
root = tk.Tk()
root.title("Quiz Management System")
root.geometry("800x600")
root.resizable(False, False)

# Header
header_frame = tk.Frame(root, bg="#1976d2", height=80)
header_frame.pack(fill="x")
header_frame.pack_propagate(False)
tk.Label(header_frame, text="Quiz Management System", font=("Arial", 18, "bold"), bg="#1976d2", fg="white").pack(pady=20)

# Student info
info_frame = tk.Frame(root, bg="#e3f2fd")
info_frame.pack(fill="x", pady=10)
tk.Label(info_frame, text="Welcome, Student: Taghreed Mohammed", font=("Arial", 14, "bold"), bg="#e3f2fd").pack(pady=10)
tk.Label(info_frame, text="ID: 441234567 | Faculty: Engineering | Department: Computer Science", 
         font=("Arial", 10), bg="#e3f2fd").pack(pady=2)

# Available quizzes
quiz_frame = ttk.LabelFrame(root, text="Available Quizzes")
quiz_frame.pack(fill="both", expand=True, padx=20, pady=10)

quizzes_data = [
    ("Physics Quiz", "Chapter 1 - Motion", "15 min", "Available"),
    ("Math Quiz", "Calculus", "10 min", "Available"),
    ("Chemistry Quiz", "Periodic Table", "20 min", "Available"),
    ("English Quiz", "Basic Grammar", "12 min", "Completed")
]

headers_frame = tk.Frame(quiz_frame)
headers_frame.pack(fill="x", padx=10, pady=5)
tk.Label(headers_frame, text="Quiz Name", font=("Arial", 10, "bold"), width=15).pack(side="left")
tk.Label(headers_frame, text="Topic", font=("Arial", 10, "bold"), width=20).pack(side="left")
tk.Label(headers_frame, text="Duration", font=("Arial", 10, "bold"), width=10).pack(side="left")
tk.Label(headers_frame, text="Status", font=("Arial", 10, "bold"), width=10).pack(side="left")

for quiz_name, topic, duration, status in quizzes_data:
    row = tk.Frame(quiz_frame, relief="ridge", bd=1)
    row.pack(fill="x", padx=10, pady=2)

    tk.Label(row, text=quiz_name, font=("Arial", 10), width=15).pack(side="left", padx=5, pady=5)
    tk.Label(row, text=topic, font=("Arial", 9), width=20).pack(side="left", padx=5)
    tk.Label(row, text=duration, font=("Arial", 9), width=10).pack(side="left", padx=5)

    status_color = "green" if status == "Available" else "gray"
    tk.Label(row, text=status, font=("Arial", 9, "bold"), width=10, fg=status_color).pack(side="left", padx=5)

    if status == "Available":
        ttk.Button(row, text="Start Quiz", command=lambda q=quiz_name: start_quiz(q)).pack(side="right", padx=10, pady=2)
    else:
        ttk.Button(row, text="Completed", state="disabled").pack(side="right", padx=10, pady=2)

# Status section
status_frame = tk.LabelFrame(root, text="System Status")
status_frame.pack(fill="x", padx=20, pady=10)
status_inner = tk.Frame(status_frame)
status_inner.pack(pady=10)

monitor_frame = tk.Frame(status_inner)
monitor_frame.pack(anchor="w")
tk.Label(monitor_frame, text="Monitoring System:", font=("Arial", 10)).pack(side="left")
status_label = tk.Label(monitor_frame, text="Inactive", fg="red", font=("Arial", 10, "bold"))
status_label.pack(side="left", padx=5)

system_frame = tk.Frame(status_inner)
system_frame.pack(anchor="w", pady=5)
tk.Label(system_frame, text="System:", font=("Arial", 10)).pack(side="left")
tk.Label(system_frame, text="Ready", fg="green", font=("Arial", 10, "bold")).pack(side="left", padx=5)

def update_status():
    global monitoring_thread
    try:
        if monitoring_thread and monitoring_thread.is_alive():
            status_label.config(text="Active - Monitoring", fg="green")
        else:
            status_label.config(text="Inactive", fg="red")
    except Exception as e:
        status_label.config(text="Error", fg="orange")
        print(f"Status update error: {e}")
    root.after(2000, update_status)

# Control buttons
control_frame = tk.Frame(root)
control_frame.pack(pady=15)

def start_monitoring_manually():
    global monitoring_thread
    if monitoring_thread is None or not monitoring_thread.is_alive():
        monitoring_thread = threading.Thread(target=run_the_back, daemon=True)
        monitoring_thread.start()
        messagebox.showinfo("Info", "Monitoring system started manually")
    else:
        messagebox.showinfo("Warning", "Monitoring system is already running")

def show_help():
    help_window = tk.Toplevel()
    help_window.title("Help")
    help_window.geometry("500x400")
    help_text = """
Monitoring System:
- Activated automatically when any quiz starts
- Records camera and audio
- Tracks mouse and keyboard movements
- Takes screenshots periodically

Quizzes:
- Select the desired quiz
- Read instructions carefully
- Answer all questions before submitting
- Watch the time limit

Important:
- Do not close the window during the quiz
- Do not use other applications
- Ensure camera is connected
- Press ESC to stop monitoring

Support:
Email: support@university.edu.sa
Phone: 123-456-7890
    """
    tk.Label(help_window, text=help_text, font=("Arial", 10), justify="left").pack(padx=20, pady=20)

ttk.Button(control_frame, text="Start Monitoring Manually", command=start_monitoring_manually).pack(side="left", padx=5)
ttk.Button(control_frame, text="Help", command=show_help).pack(side="left", padx=5)
ttk.Button(control_frame, text="Logout", command=root.quit).pack(side="left", padx=5)

# Footer
footer_frame = tk.Frame(root, bg="#f5f5f5", height=30)
footer_frame.pack(fill="x", side="bottom")
footer_frame.pack_propagate(False)
tk.Label(footer_frame, text="© 2024 University - All rights reserved", font=("Arial", 8), bg="#f5f5f5").pack(pady=5)

# Start status updates
update_status()
root.mainloop()
