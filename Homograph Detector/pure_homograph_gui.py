import tkinter as tk
from tkinter import messagebox, filedialog
from confusables import is_confusable, confusable_characters
import time

# ---------------- Detection Logic ---------------- #

def get_confusable_details(text):
    confusables = []
    for ch in text:
        if ch.isalpha() and is_confusable(ch):
            try:
                details = confusable_characters(ch)
                confusables.append((ch, details))
            except Exception:
                confusables.append((ch, "Confusable"))
    return confusables

def is_homograph_string(text):
    return any(ch.isalpha() and is_confusable(ch) for ch in text)

def log_result(text, confusables):
    with open("string_scan_log.txt", "a", encoding="utf-8") as log:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log.write(f"\n[{timestamp}] Scanned: {text}\n")
        for ch, targets in confusables:
            if isinstance(targets, list):
                target_str = ", ".join(targets)
            else:
                target_str = str(targets)
            log.write(f"   - '{ch}' is confusable with: {target_str}\n")

# ---------------- GUI Actions ---------------- #

def scan_input():
    text = input_entry.get().strip()
    if not text:
        result_label.config(text="⚠️ Please enter text.", fg="orange")
        return

    if is_homograph_string(text):
        confusables = get_confusable_details(text)
        result_label.config(text=f"⚠️ Suspicious characters found!", fg="red")
        show_details(confusables)
        log_result(text, confusables)
    else:
        result_label.config(text="✅ No suspicious characters found.", fg="green")
        log_result(text, [])

def show_details(confusables):
    message = ""
    for ch, similar in confusables:
        if isinstance(similar, list):
            similar_text = ", ".join(similar)
        else:
            similar_text = str(similar)
        message += f"'{ch}' looks like: {similar_text}\n"
    messagebox.showwarning("Suspicious Characters Found", message)

def scan_from_file():
    path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not path:
        return

    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    total_suspicious = 0
    for line in lines:
        if is_homograph_string(line):
            confusables = get_confusable_details(line)
            log_result(line, confusables)
            total_suspicious += 1
        else:
            log_result(line, [])

    if total_suspicious:
        messagebox.showwarning("Scan Complete", f"⚠️ {total_suspicious} suspicious lines found!")
    else:
        messagebox.showinfo("Scan Complete", "✅ No suspicious lines found.")

def clear_input():
    input_entry.delete(0, tk.END)
    result_label.config(text="")

def exit_app():
    root.destroy()

# ---------------- GUI Setup ---------------- #

root = tk.Tk()
root.title("🛡️ Pure Homograph Detector")
root.geometry("600x320")
root.configure(bg="#f0f0f0")
root.resizable(False, False)

FONT = ("Segoe UI", 12)
TITLE_FONT = ("Segoe UI", 16, "bold")

tk.Label(root, text="Pure Homograph Detector", font=TITLE_FONT, bg="#f0f0f0").pack(pady=10)

frame = tk.Frame(root, bg="#f0f0f0")
frame.pack(pady=5)

input_entry = tk.Entry(frame, font=FONT, width=50)
input_entry.pack(side="left", padx=5)
input_entry.bind("<Return>", lambda event: scan_input())

scan_btn = tk.Button(frame, text="Scan", command=scan_input, font=FONT, bg="#d9f9d9", width=10)
scan_btn.pack(side="left", padx=5)

result_label = tk.Label(root, text="", font=FONT, bg="#f0f0f0")
result_label.pack(pady=10)

action_frame = tk.Frame(root, bg="#f0f0f0")
action_frame.pack(pady=5)

tk.Button(action_frame, text="Scan From File", command=scan_from_file, font=FONT, bg="#def", width=15).pack(side="left", padx=10)
tk.Button(action_frame, text="Clear", command=clear_input, font=FONT, bg="#eee", width=10).pack(side="left", padx=10)
tk.Button(action_frame, text="Exit", command=exit_app, font=FONT, bg="#fcc", width=10).pack(side="left", padx=10)

root.mainloop()
