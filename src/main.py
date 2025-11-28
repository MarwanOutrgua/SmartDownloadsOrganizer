import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import shutil
import threading
import time
from datetime import datetime

# ===========================
# CONFIGURATION & THEME
# ===========================
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# ===========================
# FUNCTIONS
# ===========================
def log_move(file_name, category):
    try:
        log_path = Path(folder_path_var.get()) / "organize_log.txt"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -> {file_name} -> {category}\n")
    except Exception as e:
        print(f"Error logging: {e}")

def organize_files(folder_path, textbox_widget):
    folder_path = Path(folder_path)
    if not folder_path.exists():
        return

    files = [f for f in folder_path.iterdir() if f.is_file() and f.name != "organize_log.txt"]

    categories = {
        "Images": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg"],
        "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".doc", ".csv"],
        "Videos": [".mp4", ".mkv", ".avi", ".mov", ".flv"],
        "Softwares": [".exe", ".msi", ".iso", ".dmg"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "Music": [".mp3", ".wav", ".flac"],
        "Code": [".py", ".js", ".html", ".css", ".java", ".cpp"],
        "Others": []
    }

    files_by_category = {key: [] for key in categories}

    for file in files:
        ext = file.suffix.lower()
        found = False
        for category, extensions in categories.items():
            if ext in extensions:
                files_by_category[category].append(file.name)
                found = True
                break
        if not found:
            files_by_category["Others"].append(file.name)

    total_files = sum(len(v) for v in files_by_category.values())
    
    if total_files == 0:
        if textbox_widget:
            textbox_widget.insert("end", "No files to organize.\n")
        progress_bar.set(1.0)
        return

    count = 0
    progress_bar.set(0.0)

    for category, items in files_by_category.items():
        if not items:
            continue
        
        category_folder = folder_path / category
        category_folder.mkdir(exist_ok=True)
        
        for file_name in items:
            src = folder_path / file_name
            dst = category_folder / file_name

            # Handle duplicates
            i = 1
            while dst.exists():
                dst = category_folder / f"{dst.stem}({i}){dst.suffix}"
                i += 1

            try:
                shutil.move(str(src), str(dst))
                log_move(file_name, category)
                
                count += 1
                
                # Update GUI
                if textbox_widget:
                    textbox_widget.insert("end", f"Moved: {file_name} -> {category}\n")
                    textbox_widget.see("end")
                
                # CustomTkinter progress bar works from 0.0 to 1.0
                progress_bar.set(count / total_files)
                root.update_idletasks()
                
            except Exception as e:
                if textbox_widget:
                    textbox_widget.insert("end", f"Error moving {file_name}: {e}\n")

def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path_var.set(folder_selected)

def start_organize():
    folder = folder_path_var.get()
    if folder:
        # CTkTextbox delete uses specific string indices
        text_widget.delete("0.0", "end") 
        organize_files(folder, text_widget)
        messagebox.showinfo("Done", "Files have been organized manually!")
    else:
        messagebox.showwarning("Warning", "Please select a folder first.")

# ===========================
# AUTO-ORGANIZE THREAD (SMART)
# ===========================
auto_organize_running = False
auto_thread = None

def auto_organize_loop():
    global auto_organize_running
    last_run_date = None
    
    while auto_organize_running:
        now = datetime.now()
        today = now.date()
        folder = folder_path_var.get()
        
        target_hour = int(auto_time_hour_var.get())
        
        # Check if conditions are met
        if folder and last_run_date != today and now.hour >= target_hour:
            # We must use root.after to update GUI from a thread safely, 
            # or just run the file logic since organize_files handles GUI updates via update_idletasks
            # ideally, purely logic should be here, but for this simple app:
            organize_files(folder, None) # None passed as text_widget to avoid threading conflict on Textbox
            last_run_date = today
            print(f"Auto-organized at {now}")
            
        time.sleep(30)  # check every 30 seconds

def toggle_auto_organize():
    global auto_organize_running, auto_thread
    
    if auto_organize_running:
        auto_organize_running = False
        toggle_btn.configure(text="Start Auto-Organize", fg_color="green", hover_color="#006400")
        status_label.configure(text="Status: Stopped", text_color="red")
    else:
        folder = folder_path_var.get()
        if not folder:
            messagebox.showwarning("Warning", "Select a folder first!")
            return
            
        auto_organize_running = True
        auto_thread = threading.Thread(target=auto_organize_loop, daemon=True)
        auto_thread.start()
        
        toggle_btn.configure(text="Stop Auto-Organize", fg_color="red", hover_color="#8B0000")
        target_h = auto_time_hour_var.get()
        status_label.configure(text=f"Status: Running (Daily at {target_h}:00)", text_color="green")

# ===========================
# GUI SETUP
# ===========================
root = ctk.CTk()
root.title("Smart Downloads Organizer")
root.geometry("750x600")

# Variables
folder_path_var = tk.StringVar()
auto_time_hour_var = tk.StringVar(value="16") # Default hour

# 1. Header / Folder Selection
frame_top = ctk.CTkFrame(root)
frame_top.pack(pady=20, padx=20, fill="x")

ctk.CTkLabel(frame_top, text="Select Folder:", font=("Arial", 14, "bold")).pack(side="left", padx=10)
entry_path = ctk.CTkEntry(frame_top, textvariable=folder_path_var, width=400, placeholder_text="Path to folder...")
entry_path.pack(side="left", padx=10)
ctk.CTkButton(frame_top, text="Browse", command=select_folder, width=100).pack(side="left")

# 2. Manual Action
frame_manual = ctk.CTkFrame(root)
frame_manual.pack(pady=10, padx=20, fill="x")

ctk.CTkLabel(frame_manual, text="Manual Mode:", font=("Arial", 14, "bold")).pack(pady=(10, 5))
ctk.CTkButton(frame_manual, text="Organize Now", command=start_organize, 
              fg_color="#1f538d", height=40, font=("Arial", 14)).pack(pady=10, fill="x", padx=100)

# 3. Auto-Organize Settings
frame_auto = ctk.CTkFrame(root)
frame_auto.pack(pady=10, padx=20, fill="x")

ctk.CTkLabel(frame_auto, text="Auto-Organize Settings:", font=("Arial", 14, "bold")).pack(pady=(10, 5))

frame_time = ctk.CTkFrame(frame_auto, fg_color="transparent")
frame_time.pack(pady=5)

ctk.CTkLabel(frame_time, text="Run daily after hour:").pack(side="left", padx=5)
# Replacing Spinbox with OptionMenu for cleaner CTk look
hours = [str(i).zfill(2) for i in range(24)]
time_menu = ctk.CTkOptionMenu(frame_time, values=hours, variable=auto_time_hour_var, width=70)
time_menu.pack(side="left", padx=5)

toggle_btn = ctk.CTkButton(frame_auto, text="Start Auto-Organize", command=toggle_auto_organize, 
                           fg_color="green", hover_color="#006400")
toggle_btn.pack(pady=10)

status_label = ctk.CTkLabel(frame_auto, text="Status: Stopped", text_color="gray")
status_label.pack(pady=5)

# 4. Logs & Progress
frame_logs = ctk.CTkFrame(root)
frame_logs.pack(pady=10, padx=20, fill="both", expand=True)

progress_bar = ctk.CTkProgressBar(frame_logs, width=600)
progress_bar.pack(pady=10)
progress_bar.set(0)

ctk.CTkLabel(frame_logs, text="Activity Log:").pack(anchor="w", padx=10)
text_widget = ctk.CTkTextbox(frame_logs, width=600, height=150)
text_widget.pack(pady=(0, 10), padx=10, fill="both", expand=True)

root.mainloop()