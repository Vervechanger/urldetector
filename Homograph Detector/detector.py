import idna
from confusables import is_confusable
import tkinter as tk
from tkinter import messagebox


def is_homograph(domain: str) -> bool:
    try:
        ascii_version = idna.encode(domain).decode('ascii')
        if domain == ascii_version:
            return False  # Pure ASCII domain, likely safe
    except Exception:
        return True  # Punycode error or suspicious IDN

    # Check for confusable characters
    for ch in domain:
        if is_confusable(ch, preferred_aliases=["LATIN"]):
            return True

    return False


def check_domain(event=None):
    domain = domain_entry.get().strip()
    if not domain:
        result_label.config(text="⚠️ Please enter a domain name", fg="orange")
        return

    try:
        if is_homograph(domain):
            result_label.config(
                text=f"⚠️ Suspicious domain detected:\n{domain}", fg="red"
            )
        else:
            result_label.config(
                text=f"✅ Domain looks safe:\n{domain}", fg="green"
            )
    except Exception as e:
        result_label.config(text=f"❌ Error: {e}", fg="red")


def clear_input():
    domain_entry.delete(0, tk.END)
    result_label.config(text="")


def exit_app():
    root.destroy()


# GUI setup
root = tk.Tk()
root.title("🔍 Homograph Attack Detector")
root.geometry("500x260")
root.resizable(False, False)
root.configure(bg="#f7f7f7")

# Fonts
FONT = ("Segoe UI", 12)
TITLE_FONT = ("Segoe UI", 16, "bold")

# Title
title_label = tk.Label(root, text="Homograph Attack Detector", font=TITLE_FONT, bg="#f7f7f7")
title_label.pack(pady=10)

# Input Frame
entry_frame = tk.Frame(root, bg="#f7f7f7")
entry_frame.pack(pady=5)

domain_entry = tk.Entry(entry_frame, font=FONT, width=40)
domain_entry.pack(side="left", padx=5)
domain_entry.bind("<Return>", check_domain)
domain_entry.focus()

check_btn = tk.Button(entry_frame, text="Check", command=check_domain, font=FONT, bg="#d9f9d9", width=10)
check_btn.pack(side="left", padx=5)

# Result Label
result_label = tk.Label(root, text="", font=FONT, bg="#f7f7f7", justify="center")
result_label.pack(pady=15)

# Buttons Frame
action_frame = tk.Frame(root, bg="#f7f7f7")
action_frame.pack(pady=5)

clear_btn = tk.Button(action_frame, text="Clear", command=clear_input, font=FONT, bg="#eee", width=10)
clear_btn.pack(side="left", padx=10)

exit_btn = tk.Button_
