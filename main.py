import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext # Added scrolledtext
import subprocess
import json
import os
import sys
import threading
import time
import queue                                                  # Added queue for thread-safe communication
import pystray
from PIL import Image

HAS_PYSTRAY = True

# --- Configuration ---
CONFIG_FILE = "ollama_launcher_config.json"
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, CONFIG_FILE)

# --- Default Settings ---
# (Defaults remain the same as before)
DEFAULT_SETTINGS = {
    "ollama_exe_path": "C:/application/ollama/OLLAMA_FILE/ollama.exe",
    "variables": {
        "OLLAMA_ENABLE_CUDA": "1",
        "OLLAMA_FLASH_ATTENTION": "1",
        "CUDA_VISIBLE_DEVICES": "0,1",
        "OLLAMA_GPU_LAYERS": "999",
        "OLLAMA_HOST": "127.0.0.1:11434",
        "OLLAMA_KEEP_ALIVE": "-1",
        "OLLAMA_KV_CACHE_TYPE": "q8_0",
        "OLLAMA_MAX_QUEUE": "512",
        "OLLAMA_MODELS": "E:/LLM/ollama_models",
        "OLLAMA_NUM_PARALLEL": "1",
        "OLLAMA_ORIGINS": "*",
        "OLLAMA_TMPDIR": "E:/LLM/ollama_models/temp",
        "OLLAMA_USE_MLOCK": "1",
    }
}


class OllamaGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Ollama Launcher")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.settings = DEFAULT_SETTINGS.copy()
        self.vars = {}
        self.ollama_process = None
        self.monitor_thread = None
        # Use separate threads for reading stdout and stderr
        self.stdout_thread = None
        self.stderr_thread = None
        self.is_running = False
        # Queue for log messages from threads
        self.log_queue = queue.Queue()

        # 图标
        self.tray_icon = None    # Placeholder for the tray icon object
        self.setup_tray_icon()   # Call the setup function
        self.start_tray_thread() # Start the tray icon thread

        # --- Style ---
        style = ttk.Style()
        style.theme_use('clam')

        # --- Main Frame ---
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # Configure row/column weights for resizing
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1) # Allow content column to expand
        main_frame.columnconfigure(1, weight=1) # Allow content column to expand
        main_frame.rowconfigure(2, weight=1)    # Allow log area row to expand

        # --- Ollama Path ---
        path_frame = ttk.LabelFrame(main_frame, text="Ollama Executable Path", padding="5")
        # Span across 2 columns, adjust if needed
        path_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        path_frame.columnconfigure(1, weight=1)

        self.vars['ollama_exe_path'] = tk.StringVar()
        ttk.Label(path_frame, text="Path:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Entry(path_frame, textvariable=self.vars['ollama_exe_path'], width=60).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(path_frame, text="Browse...", command=self.browse_ollama_exe).grid(row=0, column=2, padx=5)

        # --- Environment Variables ---
        env_frame = ttk.LabelFrame(main_frame, text="Environment Variables", padding="5")
        env_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        env_frame.columnconfigure(1, weight=1) # Make entry column expandable

        # (Variable creation loop remains the same as before)
        row_num = 0
        for key, default_value in DEFAULT_SETTINGS["variables"].items():
            ttk.Label(env_frame, text=f"{key}:").grid(row=row_num, column=0, sticky=tk.W, padx=5, pady=2)
            if key in ["OLLAMA_ENABLE_CUDA", "OLLAMA_FLASH_ATTENTION", "OLLAMA_USE_MLOCK"]:
                self.vars[key] = tk.IntVar(value=int(default_value))
                ttk.Checkbutton(env_frame, variable=self.vars[key]).grid(row=row_num, column=1, sticky=tk.W, padx=5, pady=2)
            elif key in ["OLLAMA_MODELS", "OLLAMA_TMPDIR"]:
                self.vars[key] = tk.StringVar(value=default_value)
                entry_frame = ttk.Frame(env_frame)
                entry_frame.grid(row=row_num, column=1, columnspan=2, sticky=(tk.W, tk.E))
                entry_frame.columnconfigure(0, weight=1)
                ttk.Entry(entry_frame, textvariable=self.vars[key], width=50).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(5, 0))
                ttk.Button(entry_frame, text="Browse...", command=lambda k=key: self.browse_directory(k)).grid(row=0, column=1, padx=5)
            else:
                self.vars[key] = tk.StringVar(value=default_value)
                ttk.Entry(env_frame, textvariable=self.vars[key], width=50).grid(row=row_num, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=2)
            row_num += 1

        # --- Log Area ---
        log_frame = ttk.LabelFrame(main_frame, text="Ollama Log Output", padding="5")
        # Span across 2 columns, adjust row as needed
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1) # Make log area itself resizable

        self.log_widget = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15, width=80) # Adjust size
        self.log_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.log_widget.config(state=tk.DISABLED)                                                 # Make read-only initially

        # --- Buttons ---
        button_frame = ttk.Frame(main_frame, padding="5")
        # Place below log area now
        button_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        button_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self.save_button = ttk.Button(button_frame, text="Save Settings", command=self.save_settings)
        self.save_button.grid(row=0, column=0, padx=5, sticky=tk.E)

        self.start_button = ttk.Button(button_frame, text="Start Ollama", command=self.start_ollama)
        self.start_button.grid(row=0, column=1, padx=5, sticky=tk.W)

        self.stop_button = ttk.Button(button_frame, text="Stop Ollama", command=self.stop_ollama, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=2, padx=5, sticky=tk.W)

        # Optional: Keep Hide button or replace with Clear Log? Let's add Clear Log.
        self.clear_log_button = ttk.Button(button_frame, text="Clear Log", command=self.clear_log)
        self.clear_log_button.grid(row=0, column=3, padx=5, sticky=tk.W)

        # --- Status Bar ---
        self.status_var = tk.StringVar(value="Status: Idle. Load settings or configure.")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding="2")
        # Place at the bottom
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))

        # --- Load Initial Settings & Start Log Processing ---
        self.load_settings()
        self.process_log_queue() # Start checking the queue for messages

        # 菜单栏
        menubar = tk.Menu(root)
        app_menu = tk.Menu(menubar, tearoff=0)
        if HAS_PYSTRAY:
            app_menu.add_command(label="Hide to Tray", command=self.hide_window)
        app_menu.add_command(label="Exit", command=self.quit_application) # Use the new quit function
        menubar.add_cascade(label="Application", menu=app_menu)
        root.config(menu=menubar)

    # --- Methods (browse_*, load_settings, save_settings are the same) ---

    def setup_tray_icon(self):
        """Sets up the system tray icon and menu."""
        try:
            # Load the icon image - MUST exist in the script's directory
            icon_path = os.path.join(SCRIPT_DIR, "favicon.ico")
            image = Image.open(icon_path)
        except FileNotFoundError:
            messagebox.showerror("Error", "Icon file 'favicon.ico' not found in script directory. Tray icon disabled.")
            print("Error: favicon.ico not found. Cannot create tray icon.")
            HAS_PYSTRAY = False
            return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load favicon.ico: {e}. Tray icon disabled.")
            print(f"Error loading icon: {e}")
            HAS_PYSTRAY = False
            return

        # Define menu items (text, callback function)
        # IMPORTANT: Callbacks need to be wrapped to run on the main Tkinter thread using root.after
        menu = pystray.Menu(
            pystray.MenuItem(
                'Show Launcher',
                lambda: self.root.after(0, self.show_window),     # Schedule show_window
                default=True                                      # Default action on left-click
            ),
            pystray.MenuItem(
                'Start Ollama',
                lambda: self.root.after(0, self.start_ollama)     # Schedule start_ollama
            ),
            pystray.MenuItem(
                'Stop Ollama',
                lambda: self.root.after(0, self.stop_ollama)      # Schedule stop_ollama
            ),
            pystray.MenuItem(
                'Exit',
                lambda: self.root.after(0, self.quit_application) # Schedule quit_application
            ))

        # Create the icon object
        self.tray_icon = pystray.Icon("OllamaLauncher", image, "Ollama Launcher", menu)

    def start_tray_thread(self):
        """Runs the pystray icon in a separate thread."""
        if self.tray_icon:
            # Run the icon loop in a daemon thread so it exits when the main app exits
            tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            tray_thread.start()
        else:
            print("Cannot start tray thread: tray icon not set up.")

    def hide_window(self):
        """Hides the main window."""
        self.root.withdraw()
        # Optional: Notify pystray (might show a balloon tip, depending on platform)
        if self.tray_icon and self.tray_icon.HAS_NOTIFICATION:
            self.tray_icon.notify("Ollama Launcher hidden to tray.")

    def show_window(self):
        """Shows the main window from hidden state."""
        self.root.deiconify()
        self.root.lift()        # Bring window to front
        self.root.focus_force() # Force focus

    def browse_ollama_exe(self):
        path = filedialog.askopenfilename(title="Select ollama.exe", filetypes=(("Executable files", "*.exe"), ("All files", "*.*")))
        if path:
            self.vars['ollama_exe_path'].set(path)

    def browse_directory(self, key):
        path = filedialog.askdirectory(title=f"Select Directory for {key}", initialdir=self.vars[key].get() or SCRIPT_DIR)
        if path:
            self.vars[key].set(path)

    def quit_application(self):
        """Stops everything and exits the application cleanly."""
        print("Quit requested.")
        # Stop the tray icon first (signals its thread to stop)
        if self.tray_icon:
            self.tray_icon.stop()
            print("Tray icon stopped.")

        # Stop Ollama if it's running
        if self.is_running:
            print("Stopping Ollama process...")
            self.stop_ollama() # Call the existing stop function
                               # Give it a moment to process stop messages if needed
            time.sleep(0.2)

        print("Destroying Tkinter root window.")
        # Destroy the Tkinter window (ends mainloop)
        self.root.destroy()

    def load_settings(self):
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r') as f:
                    loaded_settings = json.load(f)
                self.settings = DEFAULT_SETTINGS.copy()
                self.settings.update(loaded_settings)
                if 'variables' in loaded_settings:
                    self.settings['variables'].update(loaded_settings['variables'])
                self.status_var.set("Status: Settings loaded from config.json")
            else:
                self.settings = DEFAULT_SETTINGS.copy()
                self.status_var.set("Status: config.json not found. Using default settings.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings: {e}")
            self.settings = DEFAULT_SETTINGS.copy()
            self.status_var.set("Status: Error loading settings. Using defaults.")

        self.vars['ollama_exe_path'].set(self.settings.get('ollama_exe_path', ''))
        for key, tk_var in self.vars.items():
            if key != 'ollama_exe_path' and key in self.settings['variables']:
                value = self.settings['variables'][key]
                if isinstance(tk_var, tk.IntVar):
                    try:
                        tk_var.set(int(value))
                    except (ValueError, TypeError):
                        tk_var.set(0)
                else:
                    tk_var.set(str(value))

    def save_settings(self):
        current_settings = {'ollama_exe_path': self.vars['ollama_exe_path'].get(), 'variables': {}}
        for key, tk_var in self.vars.items():
            if key != 'ollama_exe_path':
                current_settings['variables'][key] = str(tk_var.get())
        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(current_settings, f, indent=4)
            self.settings = current_settings
            self.status_var.set("Status: Settings saved to config.json")
            messagebox.showinfo("Success", "Settings saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            self.status_var.set("Status: Error saving settings.")

    def clear_log(self):
        """Clears the log text widget."""
        self.log_widget.config(state=tk.NORMAL)
        self.log_widget.delete('1.0', tk.END)
        self.log_widget.config(state=tk.DISABLED)

    def update_log(self, message):
        """Appends a message to the log widget, thread-safe via queue."""
        self.log_widget.config(state=tk.NORMAL)
        self.log_widget.insert(tk.END, message)
        self.log_widget.see(tk.END) # Auto-scroll
        self.log_widget.config(state=tk.DISABLED)

    def process_log_queue(self):
        """Checks the queue for log messages and updates the widget."""
        try:
            while True: # Process all available messages
                message = self.log_queue.get_nowait()
                self.update_log(message)
        except queue.Empty:
            pass        # No messages currently in queue
        finally:
                        # Reschedule itself to run again later
            self.root.after(100, self.process_log_queue)

    def read_output(self, pipe, pipe_name):
        """Reads lines from a pipe and puts them in the queue."""
        try:
            # Use iter to read line by line
            for line in iter(pipe.readline, ''):
                self.log_queue.put(line) # Put raw line in queue
        except Exception as e:
                                         # Log errors from the reader thread itself (optional)
            self.log_queue.put(f"--- Error reading {pipe_name}: {e} ---\n")
        finally:
            pipe.close()                 # Ensure pipe is closed when reading stops
            self.log_queue.put(f"--- {pipe_name} stream closed ---\n")

    def start_ollama(self):
        if self.is_running:
            messagebox.showwarning("Info", "Ollama is already running.")
            return

        ollama_path = self.vars['ollama_exe_path'].get()
        if not ollama_path or not os.path.exists(ollama_path):
            messagebox.showerror("Error", f"Ollama executable not found at: {ollama_path}\nPlease set the correct path and save settings.")
            self.status_var.set("Status: Error - Ollama path invalid.")
            return

        ollama_dir = os.path.dirname(ollama_path)
        env = os.environ.copy()
        for key, tk_var in self.vars.items():
            if key != 'ollama_exe_path':
                value = str(tk_var.get())
                is_flag = key in ["OLLAMA_ENABLE_CUDA", "OLLAMA_FLASH_ATTENTION", "OLLAMA_USE_MLOCK"]
                if value or is_flag:
                    env[key] = value

        try:
            self.status_var.set("Status: Starting Ollama...")
            self.clear_log() # Clear log before starting new process
            self.update_log("--- Starting Ollama Server ---\n")
            self.root.update_idletasks()

            # --- CRITICAL CHANGES for redirecting output ---
            self.ollama_process = subprocess.Popen(
                [ollama_path, "serve"],
                env=env,
                cwd=ollama_dir,
                stdout=subprocess.PIPE,             # Redirect stdout
                stderr=subprocess.PIPE,             # Redirect stderr
                text=True,                          # Decode output as text (UTF-8 default)
                encoding='utf-8',                   # Explicitly set encoding
                errors='replace',                   # Handle potential decoding errors
                bufsize=1,                          # Line buffered
                                                    # Keep CREATE_NO_WINDOW if you don't want the console popping up
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
                                                    # --- END CRITICAL CHANGES ---

            self.is_running = True
            self.status_var.set(f"Status: Ollama server running (PID: {self.ollama_process.pid})")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            # Start monitoring thread for process exit
            self.monitor_thread = threading.Thread(target=self.monitor_process_exit, daemon=True)
            self.monitor_thread.start()

            # Start threads to read stdout and stderr
            self.stdout_thread = threading.Thread(target=self.read_output, args=(self.ollama_process.stdout, "stdout"), daemon=True)
            self.stderr_thread = threading.Thread(target=self.read_output, args=(self.ollama_process.stderr, "stderr"), daemon=True)
            self.stdout_thread.start()
            self.stderr_thread.start()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start Ollama: {e}")
            self.status_var.set(f"Status: Error starting Ollama - {e}")
            self.update_log(f"--- Failed to start Ollama: {e} ---\n")
            self.is_running = False
            self.ollama_process = None
            self.start_button.config(state=tk.NORMAL) # Re-enable start button on failure

    def monitor_process_exit(self):
        """Waits for process exit and schedules GUI update."""
        exit_code = self.ollama_process.wait()
        # Process finished, schedule GUI update on main thread
        self.root.after(0, self.update_status_on_exit, exit_code)

    def update_status_on_exit(self, exit_code):
        """Called via root.after() to update GUI when process stops."""
        if self.is_running: # Check if we thought it was running
            self.is_running = False
                            # self.ollama_process is likely None or invalid now, don't rely on it
            status_message = f"Status: Ollama server stopped (Exit Code: {exit_code})."
            self.status_var.set(status_message)
            self.log_queue.put(f"--- Ollama Process Exited (Code: {exit_code}) ---\n")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
                            # Threads reading pipes should exit automatically as pipes close

    def stop_ollama(self):
        if not self.is_running or not self.ollama_process:
            self.is_running = False # Ensure state consistency
            self.ollama_process = None
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_var.set("Status: Idle (Ollama was not running).")
            return

        self.status_var.set("Status: Stopping Ollama...")
        self.update_log("--- Sending stop signal to Ollama ---\n")
        self.root.update_idletasks()

        try:
            # Important: Check if process is still alive before terminating
            if self.ollama_process.poll() is None:
                self.ollama_process.terminate()
                try:
                    self.ollama_process.wait(timeout=3)     # Wait up to 3 seconds
                except subprocess.TimeoutExpired:
                    self.update_log("--- Ollama did not terminate gracefully, killing... ---\n")
                    if self.ollama_process.poll() is None:  # Check again before kill
                        self.ollama_process.kill()
                        self.ollama_process.wait(timeout=2) # Wait for kill confirmation

            # Final check after attempts to stop
            exit_code = self.ollama_process.poll()
            self.is_running = False
            self.ollama_process = None # Clear process object
            status_msg = f"Status: Ollama server stopped (Exit Code: {exit_code})." if exit_code is not None else "Status: Ollama stopped (Exit code unknown)."
            self.status_var.set(status_msg)
            self.log_queue.put(f"--- Ollama Process Stopped (Final Code: {exit_code}) ---\n")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Error", f"Error stopping Ollama: {e}")
            self.status_var.set(f"Status: Error stopping Ollama - {e}")
            self.update_log(f"--- Error stopping Ollama: {e} ---\n")
            # Attempt to reset state even on error
            self.is_running = False
            self.ollama_process = None
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    # hide_window method removed as requested by replacing button

    def on_closing(self):
        """Handle window close button (X). Hides to tray if available."""
        if HAS_PYSTRAY and self.tray_icon:
            self.hide_window() # Hide instead of closing
        else:
                               # Fallback: Original exit behavior if tray is disabled
            if self.is_running:
                if messagebox.askyesno("Exit Confirmation", "Ollama is running. Do you want to stop it and exit?"):
                    self.stop_ollama()
                    time.sleep(0.1)
                    self.root.destroy()
            else:
                if messagebox.askyesno("Exit Confirmation", "Are you sure you want to exit?"):
                    self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = OllamaGUI(root)
    # Optional: Add back application menu if desired
    # menubar = tk.Menu(root)
    # app_menu = tk.Menu(menubar, tearoff=0)
    # # Add commands here if needed (e.g., maybe show/hide parts of UI?)
    # app_menu.add_command(label="Exit", command=app.on_closing)
    # menubar.add_cascade(label="Application", menu=app_menu)
    # root.config(menu=menubar)

    root.mainloop()
