import tkinter as tk
import unicodedata
import string
from urllib.parse import urlparse

# Whitelist — Standard US keyboard characters
standard_chars = set(
    string.ascii_letters + string.digits + string.punctuation + " "
)

# Invisible characters allowed in Notepad
safe_invisible_chars = {'\n', '\r', '\t'}

def is_allowed_standard_char(ch):
    return ch in standard_chars

def is_suspicious(ch):
    if is_allowed_standard_char(ch):
        return False
    if ch in safe_invisible_chars:
        return False
    return True

def scan_text(input_text):
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

# NEW: extract domain from a URL or return string as-is if already domain
def extract_domain(url):
    try:
        parsed = urlparse(url)
        return parsed.netloc or parsed.path  # Handles full URLs and plain domains
    except:
        return url

# NEW: scan domain or URL
def scan_domain():
    url = text_input.get("1.0", tk.END).strip()
    domain = extract_domain(url)
    results = []

    for ch in domain:
        if is_suspicious(ch):
            try:
                name = unicodedata.name(ch)
            except ValueError:
                name = "Unknown or Non-character"
            codepoint = f"U+{ord(ch):04X}"
            display_char = repr(ch) if ch.isspace() or unicodedata.category(ch).startswith("C") else ch
            results.append((display_char, name, codepoint))

    results_box.delete("1.0", tk.END)
    results_box.insert(tk.END, f"🔍 Scanning domain: {domain}\n\n")

    if results:
        results_box.insert(tk.END, "⚠️ Suspicious characters found in domain:\n\n")
        for ch, name, codepoint in results:
            results_box.insert(tk.END, f"{ch} — {name} ({codepoint})\n")
    else:
        results_box.insert(tk.END, "✅ Domain appears clean.\n")

# Clipboard monitoring
last_clipboard = ""

def monitor_clipboard():
    global last_clipboard
    try:
        current = root.clipboard_get()
        if current != last_clipboard:
            last_clipboard = current
            scan_text(current)
    except tk.TclError:
        pass  # Clipboard is empty or not text
    root.after(1000, monitor_clipboard)  # Check again in 1 second

# GUI layout
root = tk.Tk()
root.title("Homograph Attack Detector with Clipboard and URL Monitor")

tk.Label(root, text="Manual Input (text or URL):").pack(pady=5)

text_input = tk.Text(root, height=5, width=60)
text_input.pack(pady=5)

# Buttons
scan_btn = tk.Button(root, text="Scan Input Text", command=lambda: scan_text(text_input.get("1.0", tk.END)))
scan_btn.pack(pady=5)

scan_domain_btn = tk.Button(root, text="Scan Domain or URL", command=scan_domain)
scan_domain_btn.pack(pady=5)

results_box = tk.Text(root, height=15, width=90, fg="red")
results_box.pack(pady=5)

# Start clipboard monitoring
monitor_clipboard()

root.mainloop()
