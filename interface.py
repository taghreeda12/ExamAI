import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import datetime

app = ttk.Window(themename="cyborg")
app.title("نظام مراقبة الامتحانات")
app.geometry("800x600")


monitoring = tk.BooleanVar(value=False)
face_detected = tk.BooleanVar()
sound_detected = tk.BooleanVar()
mouse_active = tk.BooleanVar()
eye_contact = tk.BooleanVar()

title_label = ttk.Label(app, text="نظام مراقبة الامتحانات بالذكاء الاصطناعي", font=("Helvetica", 18, "bold"), bootstyle="info")
title_label.pack(pady=10)


frame = ttk.Labelframe(app, text="خيارات المراقبة", padding=20, bootstyle="primary")
frame.pack(pady=20, fill=X, padx=20)


ttk.Checkbutton(frame, text="كشف الوجه والعين", variable=face_detected, bootstyle="success").pack(anchor=W, pady=5)
ttk.Checkbutton(frame, text="كشف الصوت", variable=sound_detected, bootstyle="success").pack(anchor=W, pady=5)
ttk.Checkbutton(frame, text="مراقبة الماوس والكيبورد", variable=mouse_active, bootstyle="success").pack(anchor=W, pady=5)
ttk.Checkbutton(frame, text="متابعة تركيز النظر", variable=eye_contact, bootstyle="success").pack(anchor=W, pady=5)


def toggle_monitoring():
    monitoring.set(not monitoring.get())
    if monitoring.get():
        start_btn.config(text="إيقاف المراقبة", bootstyle="danger")
        status_label.config(text="🟢 المراقبة قيد التشغيل", bootstyle="success")
    else:
        start_btn.config(text="ابدأ المراقبة", bootstyle="info")
        status_label.config(text="🔴 المراقبة متوقفة", bootstyle="danger")

start_btn = ttk.Button(app, text="ابدأ المراقبة", command=toggle_monitoring, bootstyle="info-outline")
start_btn.pack(pady=10)


status_label = ttk.Label(app, text="🔴 المراقبة متوقفة", font=("Helvetica", 12))
status_label.pack()

def analyze():
    report = "📋 تقرير المراقبة:\n"
    report += f"- كشف الوجه والعين: {'✅' if face_detected.get() else '❌'}\n"
    report += f"- كشف الصوت: {'✅' if sound_detected.get() else '❌'}\n"
    report += f"- مراقبة الماوس والكيبورد: {'✅' if mouse_active.get() else '❌'}\n"
    report += f"- متابعة النظر: {'✅' if eye_contact.get() else '❌'}\n"
    messagebox.showinfo("تحليل البيانات", report)

ttk.Button(app, text="تحليل الحالة", command=analyze, bootstyle="warning-outline").pack(pady=10)


def save_report():
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    content = f"""تقرير مراقبة الامتحان - {now}
=========================
كشف الوجه والعين: {face_detected.get()}
كشف الصوت: {sound_detected.get()}
مراقبة الماوس والكيبورد: {mouse_active.get()}
متابعة النظر: {eye_contact.get()}
حالة النظام: {"نشط" if monitoring.get() else "متوقف"}
"""
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=f"report_{now}.txt")
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        messagebox.showinfo("تم الحفظ", f"تم حفظ التقرير في:\n{file_path}")

ttk.Button(app, text="💾 حفظ التقرير", command=save_report, bootstyle="success").pack(pady=10)


ttk.Button(app, text="خروج", command=app.destroy, bootstyle="danger-outline").pack(pady=10)


app.mainloop()
