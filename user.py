# =============================================================================
# user.py - Quiz Interface with Monitoring
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from basemodel import run_the_back
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variable to track monitoring thread
monitoring_thread = None

# === الكويز الحقيقي ===
def start_real_quiz(title):
    global monitoring_thread
    
    # Start monitoring in background thread
    if monitoring_thread is None or not monitoring_thread.is_alive():
        logging.info("🔍 Starting monitoring system...")
        monitoring_thread = threading.Thread(target=run_the_back, daemon=True)
        monitoring_thread.start()
        logging.info("🔍 Monitoring system started.")
    else:
        logging.info("🔍 Monitoring system is already running.")

    quiz_window = tk.Toplevel()
    quiz_window.title(f"الكويز - {title}")
    quiz_window.geometry("500x400")
    quiz_window.resizable(False, False)

    # Quiz header
    header_frame = tk.Frame(quiz_window, bg="lightblue")
    header_frame.pack(fill="x")
    tk.Label(header_frame, text=f"🎯 {title}", font=("Arial", 16, "bold"), bg="lightblue").pack(pady=10)
    
    # Warning message about monitoring
    warning_frame = tk.Frame(quiz_window, bg="#ffeb3b", relief="solid", bd=2)
    warning_frame.pack(fill="x", padx=10, pady=10)
    tk.Label(warning_frame, text="⚠️ تم تفعيل نظام المراقبة أثناء الكويز", 
             bg="#ffeb3b", font=("Arial", 10, "bold"), fg="red").pack(pady=5)
    tk.Label(warning_frame, text="سيتم تسجيل جميع الأنشطة والحركات", 
             bg="#ffeb3b", font=("Arial", 9)).pack(pady=2)

    # Question frame
    question_frame = tk.LabelFrame(quiz_window, text="السؤال الأول", font=("Arial", 12, "bold"))
    question_frame.pack(fill="both", expand=True, padx=20, pady=10)

    tk.Label(question_frame, text="ما هي عاصمة جمهورية مصر العربية؟", 
             font=("Arial", 12), wraplength=400).pack(pady=15)

    answer = tk.StringVar()
    
    # Answer options
    options = [
        ("القاهرة", "القاهرة"),
        ("الإسكندرية", "الإسكندرية"), 
        ("الجيزة", "الجيزة"),
        ("الخرطوم", "الخرطوم")
    ]
    
    for text, value in options:
        ttk.Radiobutton(question_frame, text=text, variable=answer, 
                       value=value, style="TRadiobutton").pack(anchor="w", padx=40, pady=3)

    # Timer display
    timer_frame = tk.Frame(quiz_window)
    timer_frame.pack(pady=5)
    tk.Label(timer_frame, text="الوقت المتبقي:", font=("Arial", 10)).pack(side="left")
    timer_label = tk.Label(timer_frame, text="05:00", font=("Arial", 10, "bold"), fg="green")
    timer_label.pack(side="left", padx=5)

    # Timer countdown
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
            timer_label.config(text="انتهى الوقت!", fg="red")
            submit_real_quiz()

    def submit_real_quiz():
        if not answer.get():
            messagebox.showwarning("تنبيه", "يجب اختيار إجابة قبل التسليم!")
            return
        
        # Check the answer
        if answer.get() == "القاهرة":
            messagebox.showinfo("نتيجة الكويز", "✔️ إجابة صحيحة!\nالدرجة: 10/10\nتم تسليم الكويز بنجاح.")
        else:
            messagebox.showinfo("نتيجة الكويز", f"❌ إجابة خاطئة!\nالإجابة الصحيحة: القاهرة\nإجابتك: {answer.get()}\nالدرجة: 0/10")
        
        quiz_window.destroy()

    # Buttons frame
    button_frame = tk.Frame(quiz_window)
    button_frame.pack(pady=15)
    
    ttk.Button(button_frame, text="تسليم الكويز", command=submit_real_quiz).pack(side="left", padx=10)
    ttk.Button(button_frame, text="إلغاء", command=quiz_window.destroy).pack(side="left", padx=10)

    # Start timer
    update_timer()

# === عند الضغط على "ابدأ كويز" ===
def start_quiz(title):
    response = messagebox.askyesno("تأكيد بدء الكويز", 
                                 f"هل تريد بدء الكويز: {title}؟\n\n"
                                 "⚠️ ملاحظة مهمة:\n"
                                 "• سيتم تفعيل نظام المراقبة تلقائياً\n"
                                 "• سيتم تسجيل الكاميرا والصوت\n"
                                 "• سيتم تتبع حركات الماوس والكيبورد\n"
                                 "• الوقت المحدد: 5 دقائق\n\n"
                                 "هل تريد المتابعة؟")
    if response:
        start_real_quiz(title)

# === الواجهة الرئيسية ===
root = tk.Tk()
root.title("نظام إدارة الكويزات - جامعة الملك سعود")
root.geometry("800x600")
root.resizable(False, False)

# Header
header_frame = tk.Frame(root, bg="#1976d2", height=80)
header_frame.pack(fill="x")
header_frame.pack_propagate(False)

tk.Label(header_frame, text="🎓 نظام إدارة الكويزات", 
         font=("Arial", 18, "bold"), bg="#1976d2", fg="white").pack(pady=20)

# Student info
info_frame = tk.Frame(root, bg="#e3f2fd")
info_frame.pack(fill="x", pady=10)
tk.Label(info_frame, text="📘 مرحبًا، الطالب: تغريده محمد علي", 
         font=("Arial", 14, "bold"), bg="#e3f2fd").pack(pady=10)
tk.Label(info_frame, text="الرقم الجامعي: 441234567 | الكلية: الهندسة | القسم: علوم الحاسب", 
         font=("Arial", 10), bg="#e3f2fd").pack(pady=2)

# === الكويزات ===
quiz_frame = ttk.LabelFrame(root, text="📝 الكويزات المتاحة", style="Quiz.TLabelframe")
quiz_frame.pack(fill="both", expand=True, padx=20, pady=10)

quizzes_data = [
    ("كويز فيزياء", "الفصل الأول - الحركة", "15 دقيقة", "متاح"),
    ("كويز رياضيات", "التفاضل والتكامل", "10 دقائق", "متاح"),
    ("كويز كيمياء", "الجدول الدوري", "20 دقيقة", "متاح"),
    ("كويز انجليزي", "القواعد الأساسية", "12 دقيقة", "مكتمل")
]

# Headers
headers_frame = tk.Frame(quiz_frame)
headers_frame.pack(fill="x", padx=10, pady=5)
tk.Label(headers_frame, text="اسم الكويز", font=("Arial", 10, "bold"), width=15).pack(side="left")
tk.Label(headers_frame, text="الموضوع", font=("Arial", 10, "bold"), width=20).pack(side="left")
tk.Label(headers_frame, text="المدة", font=("Arial", 10, "bold"), width=10).pack(side="left")
tk.Label(headers_frame, text="الحالة", font=("Arial", 10, "bold"), width=10).pack(side="left")

# Quiz rows
for quiz_name, topic, duration, status in quizzes_data:
    row = tk.Frame(quiz_frame, relief="ridge", bd=1)
    row.pack(fill="x", padx=10, pady=2)
    
    tk.Label(row, text=f"📋 {quiz_name}", font=("Arial", 10), width=15).pack(side="left", padx=5, pady=5)
    tk.Label(row, text=topic, font=("Arial", 9), width=20).pack(side="left", padx=5)
    tk.Label(row, text=duration, font=("Arial", 9), width=10).pack(side="left", padx=5)
    
    status_color = "green" if status == "متاح" else "gray"
    tk.Label(row, text=status, font=("Arial", 9, "bold"), width=10, fg=status_color).pack(side="left", padx=5)
    
    if status == "متاح":
        ttk.Button(row, text="ابدأ الكويز", 
                  command=lambda q=quiz_name: start_quiz(q)).pack(side="right", padx=10, pady=2)
    else:
        ttk.Button(row, text="مكتمل", state="disabled").pack(side="right", padx=10, pady=2)

# Status indicator
status_frame = tk.LabelFrame(root, text="حالة النظام")
status_frame.pack(fill="x", padx=20, pady=10)

status_inner = tk.Frame(status_frame)
status_inner.pack(pady=10)

# Monitoring status
monitor_frame = tk.Frame(status_inner)
monitor_frame.pack(anchor="w")
tk.Label(monitor_frame, text="🔍 نظام المراقبة:", font=("Arial", 10)).pack(side="left")
status_label = tk.Label(monitor_frame, text="غير نشط", fg="red", font=("Arial", 10, "bold"))
status_label.pack(side="left", padx=5)

# System info
system_frame = tk.Frame(status_inner)
system_frame.pack(anchor="w", pady=5)
tk.Label(system_frame, text="💻 النظام:", font=("Arial", 10)).pack(side="left")
tk.Label(system_frame, text="جاهز", fg="green", font=("Arial", 10, "bold")).pack(side="left", padx=5)

def update_status():
    """Update monitoring status display"""
    global monitoring_thread
    try:
        if monitoring_thread and monitoring_thread.is_alive():
            status_label.config(text="نشط - جاري المراقبة", fg="green")
        else:
            status_label.config(text="غير نشط", fg="red")
    except Exception as e:
        status_label.config(text="خطأ في الحالة", fg="orange")
        print(f"Status update error: {e}")
    
    root.after(2000, update_status)  # Check every 2 seconds

# Control buttons
control_frame = tk.Frame(root)
control_frame.pack(pady=15)

def start_monitoring_manually():
    global monitoring_thread
    if monitoring_thread is None or not monitoring_thread.is_alive():
        monitoring_thread = threading.Thread(target=run_the_back, daemon=True)
        monitoring_thread.start()
        messagebox.showinfo("تم", "تم تشغيل نظام المراقبة يدوياً")
    else:
        messagebox.showinfo("تنبيه", "نظام المراقبة يعمل بالفعل")

def show_help():
    help_window = tk.Toplevel()
    help_window.title("المساعدة")
    help_window.geometry("500x400")
    
    help_text = """
🔍 نظام المراقبة:
• يتم تفعيله تلقائياً عند بدء أي كويز
• يسجل الكاميرا والصوت
• يتتبع حركات الماوس والكيبورد
• يأخذ لقطات دورية كل 20 ثانية

📝 الكويزات:
• اختر الكويز المطلوب
• اقرأ التعليمات بعناية
• املأ جميع الإجابات قبل التسليم
• انتبه للوقت المحدد

⚠️ تعليمات مهمة:
• لا تغلق النافذة أثناء الكويز
• لا تستخدم تطبيقات أخرى
• تأكد من اتصال الكاميرا
• اضغط ESC لإيقاف المراقبة

📞 الدعم الفني:
البريد: support@university.edu.sa
الهاتف: 123-456-7890
    """
    
    tk.Label(help_window, text=help_text, font=("Arial", 10), justify="right").pack(padx=20, pady=20)

ttk.Button(control_frame, text="🔍 تشغيل المراقبة يدوياً", 
           command=start_monitoring_manually).pack(side="left", padx=5)
ttk.Button(control_frame, text="❓ المساعدة", 
           command=show_help).pack(side="left", padx=5)
ttk.Button(control_frame, text="🚪 تسجيل الخروج", 
           command=root.quit).pack(side="left", padx=5)

# Footer
footer_frame = tk.Frame(root, bg="#f5f5f5", height=30)
footer_frame.pack(fill="x", side="bottom")
footer_frame.pack_propagate(False)
tk.Label(footer_frame, text="© 2024 جامعة الملك سعود - جميع الحقوق محفوظة", 
         font=("Arial", 8), bg="#f5f5f5").pack(pady=5)

# Start status updates
update_status()

root.mainloop()

# import tkinter as tk
# from tkinter import ttk, messagebox
# from basemodel import run_the_back

# # === الكويز الحقيقي ===
# def start_real_quiz(title):
#     quiz_window = tk.Toplevel()
#     quiz_window.title(f"الكويز - {title}")
#     quiz_window.geometry("400x250")

#     tk.Label(quiz_window, text=f"🎯 {title}", font=("Arial", 14, "bold")).pack(pady=10)
#     tk.Label(quiz_window, text="1. عاصمة مصر هي:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=5)

#     answer = tk.StringVar()
#     ttk.Radiobutton(quiz_window, text="القاهرة", variable=answer, value="القاهرة").pack(anchor="w", padx=40)
#     ttk.Radiobutton(quiz_window, text="الخرطوم", variable=answer, value="الخرطوم").pack(anchor="w", padx=40)

#     def submit_real_quiz():
#         if not answer.get():
#             messagebox.showwarning("تنبيه", "أجب على السؤال أولاً.")
#             return
#         messagebox.showinfo("تم", "✔️ تم تسليم الكويز. بالتوفيق!")
#         quiz_window.destroy()

#     ttk.Button(quiz_window, text="تسليم الكويز", command=submit_real_quiz).pack(pady=20)

# # === عند الضغط على "ابدأ كويز" ===
# def start_quiz(title):
#     response = messagebox.askyesno("تأكيد", f"هل تريد بدء الكويز: {title}؟")
#     if response:
#         # run_the_back()
#         start_real_quiz(title)

# # === الواجهة الرئيسية ===
# root = tk.Tk()
# root.title("لوحة الطالب")
# root.geometry("700x500")

# tk.Label(root, text="📘 مرحبًا، الطالب: تغريده محمد", font=("Arial", 16, "bold")).pack(pady=10)

# # === الكويزات ===
# quiz_frame = ttk.LabelFrame(root, text="📝 الكويزات")
# quiz_frame.pack(fill="x", padx=20, pady=10)

# quizzes = ["كويز فيزياء", "كويز رياضيات"]
# for q in quizzes:
#     row = tk.Frame(quiz_frame)
#     tk.Label(row, text=q, font=("Arial", 12)).pack(side="left", padx=10, pady=5)
#     ttk.Button(row, text="ابدأ الكويز", command=lambda q=q: start_quiz(q)).pack(side="right", padx=10)
#     row.pack(fill="x", padx=10, pady=2)

# # زر الخروج
# ttk.Button(root, text="🚪 تسجيل الخروج", command=root.quit).pack(pady=20)

# root.mainloop()


# import tkinter as tk
# from tkinter import ttk, messagebox
# import threading
# from basemodel import run_the_back

# # Global variable to track monitoring thread
# monitoring_thread = None

# # === الكويز الحقيقي ===
# def start_real_quiz(title):
#     global monitoring_thread
    
#     # Start monitoring in background thread
#     if monitoring_thread is None or not monitoring_thread.is_alive():
#         monitoring_thread = threading.Thread(target=run_the_back, daemon=True)
#         monitoring_thread.start()
#         print("🔍 تم تشغيل نظام المراقبة")

#     quiz_window = tk.Toplevel()
#     quiz_window.title(f"الكويز - {title}")
#     quiz_window.geometry("400x250")

#     tk.Label(quiz_window, text=f"🎯 {title}", font=("Arial", 14, "bold")).pack(pady=10)
#     tk.Label(quiz_window, text="1. عاصمة مصر هي:", font=("Arial", 12)).pack(anchor="w", padx=20, pady=5)

#     answer = tk.StringVar()
#     ttk.Radiobutton(quiz_window, text="القاهرة", variable=answer, value="القاهرة").pack(anchor="w", padx=40)
#     ttk.Radiobutton(quiz_window, text="الخرطوم", variable=answer, value="الخرطوم").pack(anchor="w", padx=40)

#     def submit_real_quiz():
#         if not answer.get():
#             messagebox.showwarning("تنبيه", "أجب على السؤال أولاً.")
#             return
#         messagebox.showinfo("تم", "✔️ تم تسليم الكويز. بالتوفيق!")
#         quiz_window.destroy()

#     ttk.Button(quiz_window, text="تسليم الكويز", command=submit_real_quiz).pack(pady=20)

# # === عند الضغط على "ابدأ كويز" ===
# def start_quiz(title):
#     response = messagebox.askyesno("تأكيد", f"هل تريد بدء الكويز: {title}؟")
#     if response:
#         start_real_quiz(title)

# # === الواجهة الرئيسية ===
# root = tk.Tk()
# root.title("لوحة الطالب")
# root.geometry("700x500")

# tk.Label(root, text="📘 مرحبًا، الطالب: أحمد محمد", font=("Arial", 16, "bold")).pack(pady=10)

# # === الكويزات ===
# quiz_frame = ttk.LabelFrame(root, text="📝 الكويزات")
# quiz_frame.pack(fill="x", padx=20, pady=10)

# quizzes = ["كويز فيزياء", "كويز رياضيات"]
# for q in quizzes:
#     row = tk.Frame(quiz_frame)
#     tk.Label(row, text=q, font=("Arial", 12)).pack(side="left", padx=10, pady=5)
#     ttk.Button(row, text="ابدأ الكويز", command=lambda q=q: start_quiz(q)).pack(side="right", padx=10)
#     row.pack(fill="x", padx=10, pady=2)

# # زر الخروج
# ttk.Button(root, text="🚪 تسجيل الخروج", command=root.quit).pack(pady=20)

# # Status indicator
# status_frame = tk.Frame(root)
# status_frame.pack(pady=10)
# tk.Label(status_frame, text="حالة النظام:", font=("Arial", 10)).pack(side="left")
# status_label = tk.Label(status_frame, text="غير نشط", fg="red", font=("Arial", 10, "bold"))
# status_label.pack(side="left", padx=5)

# def update_status():
#     """Update monitoring status display"""
#     global monitoring_thread
#     if monitoring_thread and monitoring_thread.is_alive():
#         status_label.config(text="نشط - جاري المراقبة", fg="green")
#     else:
#         status_label.config(text="غير نشط", fg="red")
#     root.after(2000, update_status)  # Check every 2 seconds

# # Start status updates
# update_status()

# root.mainloop()