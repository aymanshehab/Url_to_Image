# Copyright (C) 2025 Ayman Ali Shehab
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import pandas as pd
import requests

# =========================================
# Configuration & Global State
# =========================================
# Resolve base directory (EXE or script)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        BASE_DIR = os.getcwd()

# Threading Event for Control
PAUSE_EVENT = threading.Event()
# State constants
STATE_IDLE = 0
STATE_RUNNING = 1
STATE_PAUSED = 2

# =========================================
# Core Download Logic (Unchanged)
# =========================================
def download_images_from_data(data_file_path, url_column, name_column, output_folder, log_widget, control_instance):
    """Handles the main logic of loading data and downloading images."""
    
    # Start in the clear (running) state
    PAUSE_EVENT.clear() 

    # Immediately set GUI state to RUNNING on the main thread
    # This ensures the button switches from "Start Download" to "Pause" as soon as the thread begins.
    control_instance.master.after(0, lambda: control_instance._update_state(STATE_RUNNING))

    def log(message):
        log_widget.insert(tk.END, message + "\n")
        log_widget.see(tk.END) 
        log_widget.update_idletasks()

    log(f"--- Starting Download Process ---")
    log(f"Output Directory: {output_folder}")
    
    try:
        os.makedirs(output_folder, exist_ok=True)
    except Exception as e:
        log(f"❌ Error creating output folder: {e}")
        control_instance.on_completion()
        return

    # 1. Load data
    try:
        if data_file_path.lower().endswith(".csv"):
            df = pd.read_csv(data_file_path)
        elif data_file_path.lower().endswith(".xlsx"):
            df = pd.read_excel(data_file_path)
        else:
            log("❌ Unsupported file type. Use .xlsx or .csv")
            control_instance.on_completion()
            return
    except Exception as e:
        log(f"❌ Error reading file: {e}")
        control_instance.on_completion()
        return

    log(f"✅ Data loaded successfully. Total rows: {len(df)}")

    # 2. Validate columns
    if url_column not in df.columns or name_column not in df.columns:
        log("❌ Column name not found.")
        log(f"Available columns: {list(df.columns)}")
        control_instance.on_completion()
        return

    # 3. Download images
    download_count = 0
    fail_count = 0
    
    for index, row in df.iterrows():
        PAUSE_EVENT.wait() 

        name = str(row[name_column]).strip()
        url = str(row[url_column]).strip()

        if not url:
            log(f"Skipping row {index+1}: URL column is empty.")
            continue
            
        safe_name = "".join(
            c if c.isalnum() or c in ("_", "-") else "_"
            for c in name
        )

        ext = os.path.splitext(url.split("?")[0])[-1] or ".jpg"
        output_path = os.path.join(output_folder, safe_name + ext)
        
        # Simple Resume Logic (skip if file exists)
        if os.path.exists(output_path):
             log(f"Skipping: {safe_name}{ext} (Already exists)")
             download_count += 1
             continue
        
        try:
            response = requests.get(url, stream=True, timeout=15)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    PAUSE_EVENT.wait()
                    f.write(chunk)
            
            log(f"✅ Downloaded: {safe_name}{ext}")
            download_count += 1
            
        except requests.exceptions.RequestException as e:
            log(f"❌ Failed: {url} | Error: {e}")
            fail_count += 1
        except Exception as e:
            log(f"❌ An unexpected error occurred: {e}")
            fail_count += 1
            
    # --- Final Summary ---
    log("--- Download Summary ---")
    log(f"✅ Completed. Total successful downloads: {download_count}")
    
    if fail_count > 0:
        log(f"⚠️ Warning: {fail_count} downloads failed.")
    
    log(f"Output files saved to: {output_folder}")
    control_instance.on_completion()

# =========================================
# GUI Implementation (State-Machine Fixed)
# =========================================
class ImageDownloaderGUI:
    def __init__(self, master):
        self.master = master
        master.title("Bulk Image Downloader from Public URLs")
        master.geometry("700x550")
        
        style = ttk.Style(master)
        style.theme_use('clam') 

        # --- Define Colors and Variables ---
        self.SUCCESS_COLOR = '#28a745' # Green (for Start/Resume)
        self.PAUSE_COLOR = '#ffc107' # Yellow (for Pause)
        self.ERROR_COLOR = '#dc3545' # Red

        # Variables
        self.state = STATE_IDLE # Initialize state
        self.data_file_path = tk.StringVar()
        self.output_folder_path = tk.StringVar(value=os.path.join(BASE_DIR, "images"))
        self.url_column = tk.StringVar(value="URL")
        self.name_column = tk.StringVar(value="Filename")
        self.download_thread = None

        # Setup methods
        self._setup_styles(style) # Define styles before control frame
        self._setup_input_frame(master)
        self._setup_control_frame(master)
        self._setup_log_frame(master)
        
        # Ensure the button is set correctly upon startup
        self._update_state(STATE_IDLE)


    def _setup_styles(self, style):
        # Define button styles
        style.configure('Action.TButton', font=('Arial', 10, 'bold'))
        # This style handles foreground color when enabled
        style.map('Action.TButton', 
                  foreground=[('!disabled', 'black')],
                  background=[('!disabled', self.SUCCESS_COLOR)]) # Default to Green

    def _setup_input_frame(self, master):
        input_frame = ttk.LabelFrame(master, text="Configuration", padding="10 10 10 10")
        input_frame.pack(fill='x', padx=10, pady=10)

        grid_config = {'sticky': 'w', 'padx': 5, 'pady': 5}
        
        # Data File
        ttk.Label(input_frame, text="Data File (XLSX/CSV):").grid(row=0, column=0, **grid_config)
        ttk.Entry(input_frame, textvariable=self.data_file_path, width=50).grid(row=0, column=1, **grid_config)
        ttk.Button(input_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, **grid_config)

        # Output Folder Select
        ttk.Label(input_frame, text="Output Folder:").grid(row=1, column=0, **grid_config)
        ttk.Entry(input_frame, textvariable=self.output_folder_path, width=50).grid(row=1, column=1, **grid_config)
        ttk.Button(input_frame, text="Select", command=self.select_output_folder).grid(row=1, column=2, **grid_config)

        # URL Column
        ttk.Label(input_frame, text="URL Column Name:").grid(row=2, column=0, **grid_config)
        ttk.Entry(input_frame, textvariable=self.url_column, width=50).grid(row=2, column=1, **grid_config)

        # Name Column
        ttk.Label(input_frame, text="Image Name Column:").grid(row=3, column=0, **grid_config)
        ttk.Entry(input_frame, textvariable=self.name_column, width=50).grid(row=3, column=1, **grid_config)

    def _setup_control_frame(self, master):
        # --- Single Action Button ---
        control_frame = ttk.Frame(master)
        control_frame.pack(pady=10)
        
        # Use the style name defined in _setup_styles
        self.action_btn = ttk.Button(control_frame, 
                                     text="Start Download", 
                                     command=self.handle_action, 
                                     style='Action.TButton')
        self.action_btn.pack(padx=15)

    def _setup_log_frame(self, master):
        ttk.Label(master, text="Download Log:").pack(pady=(5, 0), padx=10, anchor='w')
        self.log_widget = scrolledtext.ScrolledText(master, height=12, state='disabled', wrap=tk.WORD, bg='#e9ecef', fg='#343a40', font=('Courier New', 9))
        self.log_widget.pack(padx=10, pady=5, fill='both', expand=True)

    # --- State Management ---
    def _update_state(self, new_state):
        self.state = new_state
        style = ttk.Style()
        
        # Configure button appearance based on new state
        if new_state == STATE_IDLE:
            self.action_btn.config(text="Ready")
            style.configure('Action.TButton', background=self.SUCCESS_COLOR) 
        
        elif new_state == STATE_RUNNING:
            self.action_btn.config(text="Go")
            style.configure('Action.TButton', background=self.PAUSE_COLOR) # Change to Yellow
        
        elif new_state == STATE_PAUSED:
            self.action_btn.config(text="Pause")
            style.configure('Action.TButton', background=self.SUCCESS_COLOR) # Change to Green/Success for Resume

    def handle_action(self):
        """Maps button click to the correct function based on the current state."""
        if self.state == STATE_IDLE:
            self._start_download_process()
        elif self.state == STATE_RUNNING:
            self._pause_download()
        elif self.state == STATE_PAUSED:
            self._resume_download()

    def _start_download_process(self):
        data_file = self.data_file_path.get()
        output_folder = self.output_folder_path.get()
        url_col = self.url_column.get().strip()
        name_col = self.name_column.get().strip()

        if not data_file or not url_col or not name_col or not output_folder:
            messagebox.showerror("Error", "All configuration fields must be filled.")
            return

        # Clear and configure GUI state
        self.log_widget.config(state='normal')
        self.log_widget.delete(1.0, tk.END)
        # Note: State update (IDLE -> RUNNING) is now handled by the download thread start.
        
        # Start the core logic in a thread
        self.download_thread = threading.Thread(
            target=lambda: download_images_from_data(data_file, url_col, name_col, output_folder, self.log_widget, self),
            daemon=True
        )
        self.download_thread.start() # Download thread will immediately call _update_state(STATE_RUNNING)

    def _pause_download(self):
        if not self.download_thread or not self.download_thread.is_alive():
            return
            
        PAUSE_EVENT.set() # Set the event to block the download thread
        self._update_state(STATE_PAUSED)
        self.log_widget.insert(tk.END, "▶️ Download has started.\n")
        self.log_widget.see(tk.END)

    def _resume_download(self):
        if not self.download_thread or not self.download_thread.is_alive():
            return
            
        PAUSE_EVENT.clear() # Clear the event to unblock the download thread
        self._update_state(STATE_RUNNING)
        self.log_widget.insert(tk.END, "⏸️ Paused by user.\n")
        self.log_widget.see(tk.END)

    def on_completion(self):
        """Called by the download thread when it finishes."""
        # Use after(0, ...) to ensure state update happens on the main GUI thread
        self.master.after(0, lambda: self._update_state(STATE_IDLE))
        
    # --- File/Folder Selectors (Unchanged) ---
    def browse_file(self):
        filename = filedialog.askopenfilename(
            defaultextension=".xlsx",
            filetypes=[("Data Files", "*.xlsx *.csv"), ("All files", "*.*")],
            initialdir=os.path.dirname(self.data_file_path.get()) if self.data_file_path.get() else BASE_DIR
        )
        if filename:
            self.data_file_path.set(filename)

    def select_output_folder(self):
        folder = filedialog.askdirectory(
            initialdir=self.output_folder_path.get()
        )
        if folder:
            self.output_folder_path.set(folder)

# =========================================
# Run Application
# =========================================
if __name__ == "__main__":
    try:
        import requests
        import pandas as pd
    except ImportError:
        messagebox.showerror("Error", "Required libraries 'requests' and 'pandas' are not installed. Please run 'pip install requests pandas openpyxl' and try again.")
        sys.exit(1)

    root = tk.Tk()
    app = ImageDownloaderGUI(root)
    root.mainloop()