import tkinter as tk
import unicodedata
import string

# Whitelist — Standard US keyboard characters
standard_chars = set(
    string.ascii_letters +  # A-Z, a-z
    string.digits +         # 0-9
    string.punctuation +    # ~`!@#$%^&*()-_=+[{]}\|;:'",<.>/?
    " "                     # space
)

# Invisible characters allowed by Notepad
safe_invisible_chars = {'\n', '\r', '\t'}

def is_allowed_standard_char(ch):
    return ch in standard_chars

def is_suspicious(ch):
    # Allow standard keyboard characters
    if is_allowed_standard_char(ch):
        return False
    # Allow safe hidden characters (used in Notepad)
    if ch in safe_invisible_chars:
        return False
    # Everything else is suspicious
    return True

def scan_text():
    input_text = text_input.get("1.0", tk.END)
    results = []

    for ch in input_text:
        if is_suspicious(ch):
            try:
                name = unicodedata.name(ch)
            except ValueError:
                if ch == '\n':
                    name = "LINE FEED (NEWLINE)"
                elif ch == '\r':
                    name = "CARRIAGE RETURN"
                elif ch == '\t':
                    name = "HORIZONTAL TAB"
                else:
                    name = "Unknown or Non-character"
            codepoint = f"U+{ord(ch):04X}"
            display_char = repr(ch) if ch.isspace() or unicodedata.category(ch).startswith("C") else ch
            results.append((display_char, name, codepoint))

    results_box.delete("1.0", tk.END)

    if results:
        results_box.insert(tk.END, "⚠️ Suspicious characters found:\n\n")
        for ch, name, codepoint in results:
            results_box.insert(tk.END, f"{ch} — {name} ({codepoint})\n")
    else:
        results_box.insert(tk.END, "✅ All characters are safe and standard.\n")

# GUI layout
root = tk.Tk()
root.title("Homograph Attack Detector")

tk.Label(root, text="Enter text to scan:").pack(pady=5)

text_input = tk.Text(root, height=5, width=50)
text_input.pack(pady=5)

scan_btn = tk.Button(root, text="Scan", command=scan_text)
scan_btn.pack(pady=5)

results_box = tk.Text(root, height=10, width=60, fg="red")
results_box.pack(pady=5)

root.mainloop()
