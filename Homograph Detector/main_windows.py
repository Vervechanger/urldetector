# main_windows.py
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import os, zipfile, threading, sys
from PIL import Image
import pystray
import win32com.client
from homograph_core import scan_text, scan_domain

last_clipboard = ""
tray_icon = None

# ---------------- Core Logic ----------------
def show_results(results):
    results_box.delete("1.0", tk.END)
    if not results:
        results_box.insert(tk.END, "✅ All characters are safe and standard.\n")
        return
    results_box.insert(tk.END, "⚠️ Suspicious characters found:\n\n")
    for ch, name, codepoint in results:
        display_char = repr(ch) if ch.isspace() else ch
        results_box.insert(tk.END, f"{display_char} — {name} ({codepoint})\n")

def scan_from_input():
    text = text_input.get("1.0", tk.END)
    results = scan_text(text)
    show_results(results)

def scan_domain_input():
    url = text_input.get("1.0", tk.END).strip()
    results = scan_domain(url)
    results_box.delete("1.0", tk.END)
    results_box.insert(tk.END, f"🔍 Scanning domain: {url}\n\n")
    show_results(results)

def monitor_clipboard():
    global last_clipboard
    try:
        current = root.clipboard_get()
        if current != last_clipboard:
            last_clipboard = current
            results = scan_text(current)
            show_results(results)
            if results:
                messagebox.showwarning(
                    "Suspicious Clipboard Content",
                    "⚠️ Suspicious characters detected in clipboard!"
                )
    except tk.TclError:
        pass
    root.after(1000, monitor_clipboard)

# ---------------- Export Logic ----------------
def export_results():
    data = results_box.get("1.0", tk.END).strip()
    if not data:
        messagebox.showinfo("Export", "No results to export.")
        return

    password = simpledialog.askstring("Password", "Set a password for the exported ZIP file:", show="*")
    if not password:
        messagebox.showwarning("Missing Password", "You must enter a password to export the results.")
        return

    zip_path = filedialog.asksaveasfilename(
        defaultextension=".zip",
        filetypes=[("ZIP Archive", "*.zip")],
        title="Export Password-Protected Report"
    )
    if not zip_path:
        return

    format_choice = messagebox.askquestion(
        "File Format", "Save data inside ZIP as a .csv file?\n\n(Choose 'No' for plain .txt format.)"
    )
    inner_ext = ".csv" if format_choice == "yes" else ".txt"
    inner_filename = "homograph_results" + inner_ext
    temp_path = os.path.join(os.getcwd(), inner_filename)

    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(data)

        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            zf.setpassword(password.encode("utf-8"))
            zf.write(temp_path, arcname=inner_filename)

        os.remove(temp_path)
        messagebox.showinfo("Export Complete", f"🔐 Encrypted ZIP saved:\n{zip_path}")

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        messagebox.showerror("Export Failed", f"❌ Failed to export:\n{e}")

# ---------------- Auto-Start Logic ----------------
def get_startup_shortcut_path():
    return os.path.join(os.getenv('APPDATA'), r"Microsoft\Windows\Start Menu\Programs\Startup", "HomographDetector.lnk")

def enable_autostart():
    try:
        shortcut_path = get_startup_shortcut_path()
        target = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = os.path.dirname(target)
        shortcut.IconLocation = target
        shortcut.save()

        messagebox.showinfo("Auto-Start Enabled", f"✅ App will start with Windows login.\n\nShortcut created:\n{shortcut_path}")
    except Exception as e:
        messagebox.showerror("Auto-Start Failed", f"❌ Error creating startup shortcut:\n{e}")

def disable_autostart():
    try:
        shortcut_path = get_startup_shortcut_path()
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            messagebox.showinfo("Auto-Start Disabled", "🚫 Auto-start has been disabled.")
        else:
            messagebox.showinfo("Not Found", "No auto-start shortcut was found.")
    except Exception as e:
        messagebox.showerror("Error", f"❌ Failed to disable auto-start:\n{e}")

# ---------------- Tray Icon Setup ----------------
def create_tray_icon():
    image = Image.open("icon.png")
    menu = pystray.Menu(
        pystray.MenuItem("Restore", show_window),
        pystray.MenuItem("Exit", exit_app)
    )
    icon = pystray.Icon("HomographDetector", image, "Homograph Detector", menu)
    return icon

def hide_window():
    root.withdraw()

def show_window(icon=None, item=None):
    root.after(0, root.deiconify)

def exit_app(icon=None, item=None):
    icon.stop()
    root.quit()
    sys.exit()

def on_closing():
    hide_window()

# ---------------- GUI Layout ----------------
root = tk.Tk()
root.title("Homograph Attack Detector (Windows Version)")
root.protocol("WM_DELETE_WINDOW", on_closing)

tk.Label(root, text="Paste Text or URL:").pack(pady=5)
text_input = tk.Text(root, height=5, width=60)
text_input.pack(pady=5)

tk.Button(root, text="Scan Text", command=scan_from_input).pack(pady=3)
tk.Button(root, text="Scan Domain or URL", command=scan_domain_input).pack(pady=3)
tk.Button(root, text="Export Results (Password-Protected)", command=export_results).pack(pady=3)
tk.Button(root, text="Enable Auto-Start on Boot", command=enable_autostart).pack(pady=3)
tk.Button(root, text="Disable Auto-Start", command=disable_autostart).pack(pady=3)

results_box = tk.Text(root, height=15, width=90, fg="red")
results_box.pack(pady=5)

# ---------------- Run Tray + GUI ----------------
monitor_clipboard()

def run_tray():
    global tray_icon
    tray_icon = create_tray_icon()
    tray_icon.run()

threading.Thread(target=run_tray, daemon=True).start()
root.mainloop()
