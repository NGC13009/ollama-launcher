# coding = utf-8
# Arch   = manyArch
#
# @File name:       ollama_launcher.py
# @brief:           ollama launcher 启动器主程序
# @attention:       None
# @TODO:            None
# @Author:          NGC13009
# @History:         2025-05-03		Create

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import json
import os
import sys
import threading
import time
import queue
import pystray
from PIL import Image
import re
import webbrowser
import threading
from datetime import datetime
import base64
import io     # 需要 io.BytesIO
from PIL import Image, ImageTk

from OL_resource import HELP_TEXT, VERSION, DATE, WELCONE_TEXT, about_page, help_page, icon_base64_data

has_pystray = True

# 配置文件路径
CONFIG_FILE = "ollama_launcher_config.json"
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, CONFIG_FILE)

# 默认配置
DEFAULT_SETTINGS = {
    "ollama_exe_path": "C:/application/ollama/OLLAMA_FILE/ollama.exe",
    "variables": {
        "OLLAMA_MODELS": "E:/LLM/ollama_models",
        "OLLAMA_TMPDIR": "E:/LLM/ollama_models/temp",
        "OLLAMA_HOST": "127.0.0.1:11434",
        "OLLAMA_ORIGINS": "*",
        "OLLAMA_CONTEXT_LENGTH": "2048",
        "OLLAMA_KV_CACHE_TYPE": "q8_0",
        "OLLAMA_KEEP_ALIVE": "-1",
        "OLLAMA_MAX_QUEUE": "512",
        "OLLAMA_NUM_PARALLEL": "1",
        "OLLAMA_ENABLE_CUDA": "1",
        "CUDA_VISIBLE_DEVICES": "0,1",
        "OLLAMA_FLASH_ATTENTION": "1",
        "OLLAMA_USE_MLOCK": "1",
        "OLLAMA_MULTIUSER_CACHE": "0",
        "OLLAMA_INTEL_GPU": "0",
        "OLLAMA_DEBUG": "0",
    },
    "start_minimized": False
}


# 彩色打印以支持ANSI着色
class AnsiColorText(tk.Text):

    def __init__(self, master=None, **kwargs):
        default_bg = '#1e1e1e'
        default_fg = '#efefef'

        kwargs.setdefault('background', default_bg)
        kwargs.setdefault('foreground', default_fg)
        kwargs.setdefault('insertbackground', 'white')
        kwargs.setdefault('state', tk.DISABLED)

        super().__init__(master, **kwargs)

        # Regex to find ANSI escape sequences
        self.ansi_escape_pattern = re.compile(r'\x1b\[([\d;]*)m')

        # --- Basic ANSI SGR code to Tkinter tag mapping ---
        # yapf: disable
        self.tag_configs = {
            # Reset
            '0': {'foreground': default_fg, 'background': default_bg, 'font': self._get_font_config()},

            # Styles
            '1': {'font': self._get_font_config(bold=True)},  # Bold
            '4': {'underline': True},                         # Underline
            '22': {'font': self._get_font_config(bold=False)},# Normal intensity (undo bold)
            '24': {'underline': False},                       # Not underlined

            # Foreground colors (30-37)
            '30': {'foreground': '#2e3436'},  # Black (use dark gray)
            '31': {'foreground': '#cc0000'},  # Red
            '32': {'foreground': '#4e9a06'},  # Green
            '33': {'foreground': '#c4a000'},  # Yellow
            '34': {'foreground': '#3465a4'},  # Blue
            '35': {'foreground': '#75507b'},  # Magenta
            '36': {'foreground': '#06989a'},  # Cyan
            '37': {'foreground': '#d3d7cf'},  # White (use light gray)
            '39': {'foreground': default_fg}, # Default foreground

            # --- 添加亮色前景 (90-97) ---
            '90': {'foreground': '#555753'},  # Bright Black (darker gray)
            '91': {'foreground': '#ef2929'},  # Bright Red
            '92': {'foreground': '#8ae234'},  # Bright Green
            '93': {'foreground': '#fce94f'},  # Bright Yellow
            '94': {'foreground': '#729fcf'},  # Bright Blue
            '95': {'foreground': '#ad7fa8'},  # Bright Magenta
            '96': {'foreground': '#34e2e2'},  # Bright Cyan
            '97': {'foreground': '#eeeeec'},  # Bright White

            # Background colors (40-47)
            '40': {'background': '#2e3436'},  # Black background
            '41': {'background': '#cc0000'},  # Red background
            '42': {'background': '#4e9a06'},  # Green background
            '43': {'background': '#c4a000'},  # Yellow background
            '44': {'background': '#3465a4'},  # Blue background
            '45': {'background': '#75507b'},  # Magenta background
            '46': {'background': '#06989a'},  # Cyan background
            '47': {'background': '#d3d7cf'},  # White background
            '49': {'background': default_bg}  # Default background
        }
        # yapf: enable

        # --- Configure tags ---
        for code, config in self.tag_configs.items():
            tag_name = f"ansi_{code}"
            self.tag_configure(tag_name, **config)

        # Keep track of currently active SGR codes for applying tags
        self.active_codes = {'0'} # Start with reset state
        self.lock = threading.Lock()

    def _get_font_config(self, bold=False, italic=False):
        """Gets a font configuration tuple based on the widget's default font."""
        font_str = str(self.cget('font'))
        try:
            font_parts = font_str.split()
            family = font_parts[0] if font_parts else "TkDefaultFont"
            size = int(font_parts[1]) if len(font_parts) > 1 else 10
            weight = "bold" if bold else "normal"
            slant = "italic" if italic else "roman"
            # Ensure underline is not part of the font tuple directly
            return (family, size, weight, slant)
        except Exception:
            return ("TkDefaultFont", 10, "bold" if bold else "normal", "italic" if italic else "roman")

    def write_ansi(self, text):
        """
        Inserts text containing ANSI escape codes, applying colors/styles.
        Manages widget state (NORMAL/DISABLED) and scrolling.
        """
        current_state = self.cget('state')
        self.config(state=tk.NORMAL) # Enable writing

        # Split text by ANSI codes, keeping the codes as delimiters
        parts = self.ansi_escape_pattern.split(text)

        for i, part in enumerate(parts):
            if not part: # Skip empty parts
                continue

            if i % 2 == 0:
                # This is plain text
                # Determine tags based on active codes, excluding '0' unless it's the only one
                current_tags = tuple(f"ansi_{code}" for code in self.active_codes if code != '0')
                # Use default tag 'ansi_0' if no specific codes are active
                tags_to_apply = current_tags if current_tags else ('ansi_0', )
                self.insert(tk.END, part, tags_to_apply)
            else:
                # This is an ANSI code sequence (the part inside \x1b[...m)
                if not part: # Handle case like \x1b[m (reset)
                    codes = ['0']
                else:
                    codes = part.split(';')

                # Process codes within the sequence
                needs_reset = False
                new_codes_in_sequence = set()

                for code in codes:
                    if not code: continue   # Skip empty codes from ;;
                    code = code.lstrip('0')
                    if not code: code = '0' # Treat '0' or '00' as '0'

                    if code == '0':
                        needs_reset = True
                        break # Reset overrides others in this sequence

                    if code in self.tag_configs:
                        new_codes_in_sequence.add(code)

                # Apply changes to active_codes
                if needs_reset:
                    self.active_codes = {'0'}
                else:
                    # Remove conflicting codes before adding new ones
                    temp_active = set(self.active_codes)
                    for new_code in new_codes_in_sequence:
                        if '30' <= new_code <= '37' or new_code == '39':   # Foreground
                            temp_active = {c for c in temp_active if not ('30' <= c <= '37' or c == '39')}
                        elif '40' <= new_code <= '47' or new_code == '49': # Background
                            temp_active = {c for c in temp_active if not ('40' <= c <= '47' or c == '49')}
                        elif new_code == '22':                             # Normal intensity cancels bold
                            temp_active.discard('1')
                        elif new_code == '24':                             # Not underlined cancels underline
                            temp_active.discard('4')
                                                                           # Add the new codes
                    temp_active.update(new_codes_in_sequence)
                                                                           # Ensure '0' is removed if any other code is active
                    if len(temp_active) > 1:
                        temp_active.discard('0')
                    elif not temp_active:                                  # If all codes cancelled out, reset
                        temp_active = {'0'}

                    self.active_codes = temp_active

        self.see(tk.END)                 # Scroll to the end
        self.config(state=current_state) # Restore original state (usually DISABLED)


class OllamaLauncherGUI:

    def __init__(self, root: tk.Tk):
        global has_pystray # Ensure global is accessible
        self.root = root
        bg_color = "#efefef"
        root.configure(bg=bg_color)

        self.root.title("Ollama Launcher")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Increased minsize to better accommodate the side-by-side layout
        self.root.minsize(750, 732)
        self.root.geometry("1280x752") # Adjusted default size

        try:
            icon_bytes = base64.b64decode(icon_base64_data)
            icon_stream = io.BytesIO(icon_bytes)
            pillow_image = Image.open(icon_stream)
            tk_icon = ImageTk.PhotoImage(pillow_image)
            self.root.iconphoto(True, tk_icon)
        except Exception as e:
            print(f"error when get icon: {e}")

        self.settings = DEFAULT_SETTINGS.copy()
        self.vars = {}
        self.ollama_process = None
        self.monitor_thread = None
        self.stdout_thread = None
        self.stderr_thread = None
        self.is_running = False
        self.log_queue = queue.Queue()
        self.start_minimized_var = tk.BooleanVar() # Initialized before load_settings

        # Icons - Setup before UI elements that depend on has_pystray
        self.tray_icon = None
        if has_pystray: # Only setup if library is available
            self.setup_tray_icon()
            self.start_tray_thread()

        # --- Style ---
        style = ttk.Style()
        style.theme_use('clam') # Or 'alt', 'default', 'classic'

        # --- Main Frame ---
        # 从这里开始是窗口布局相关的配置
        # This frame will contain the left panel and the right log panel
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Configure main_frame columns: col 0 for left panel, col 1 for log area
        main_frame.columnconfigure(0, weight=0) # Left panel takes needed width
        main_frame.columnconfigure(1, weight=1) # Log area expands horizontally
        main_frame.rowconfigure(0, weight=1)    # Allow the row containing panels to expand vertically

        # --- Left Panel Frame ---
        # This frame will hold path, env vars, buttons, status bar vertically
        left_panel_frame = ttk.Frame(main_frame)
        left_panel_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10)) # Add padding between panels
        left_panel_frame.columnconfigure(0, weight=1)                                         # Allow content within left panel to use width

        # --- Ollama Path (Inside Left Panel) ---
        path_frame = ttk.LabelFrame(left_panel_frame, text="Ollama Executable Path", padding="5")
        path_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5) # No columnspan needed
        path_frame.columnconfigure(1, weight=1)                       # Allow entry to expand

        self.vars['ollama_exe_path'] = tk.StringVar()
        # ttk.Label(path_frame, text="Path:").grid(row=0, column=0, sticky=tk.W, padx=5)
        # Reduced width slightly as it's in a narrower column now
        ttk.Entry(path_frame, textvariable=self.vars['ollama_exe_path'], width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(path_frame, text="/", command=self.browse_ollama_exe, width=2).grid(row=0, column=2, padx=5)

        # --- Environment Variables & Options Frame (Inside Left Panel) ---
        env_frame = ttk.LabelFrame(left_panel_frame, text="Environment Variables & Options", padding="5")
        env_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5) # No columnspan needed
        env_frame.columnconfigure(1, weight=1)                       # Make entry column expandable

        # --- Environment Variable Creation Loop ---
        row_num = 0
        for key, default_value in DEFAULT_SETTINGS["variables"].items():
            ttk.Label(env_frame, text=f"{key}:").grid(row=row_num, column=0, sticky=tk.W, padx=5, pady=2)
            if key in ["OLLAMA_ENABLE_CUDA", "OLLAMA_FLASH_ATTENTION", "OLLAMA_USE_MLOCK", "OLLAMA_DEBUG", "OLLAMA_MULTIUSER_CACHE", "OLLAMA_INTEL_GPU", "OLLAMA_DEBUG"]: # Added OLLAMA_DEBUG
                try:
                    init_val = int(default_value)
                except (ValueError, TypeError):
                    init_val = 0                                                                                                                                          # Default to 0 if conversion fails
                self.vars[key] = tk.IntVar(value=init_val)
                ttk.Checkbutton(env_frame, variable=self.vars[key]).grid(row=row_num, column=1, columnspan=2, sticky=tk.W, padx=5, pady=2)                                # Span needed for alignment
            elif key in ["OLLAMA_MODELS", "OLLAMA_TMPDIR", "OLLAMA_CONTEXT_LENGTH"]:
                self.vars[key] = tk.StringVar(value=default_value)
                entry_frame = ttk.Frame(env_frame)
                                                                                                                                                                          # Span 2 columns within env_frame grid
                entry_frame.grid(row=row_num, column=1, columnspan=2, sticky=(tk.W, tk.E))
                entry_frame.columnconfigure(0, weight=1)
                                                                                                                                                                          # Reduced width slightly
                ttk.Entry(entry_frame, textvariable=self.vars[key], width=30).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(5, 0))
                ttk.Button(entry_frame, text="/", command=lambda k=key: self.browse_directory(k), width=2).grid(row=0, column=1, padx=5)
            else:
                self.vars[key] = tk.StringVar(value=default_value)
                                                                                                                                                                          # Reduced width slightly, span 2 cols within env_frame grid
                ttk.Entry(env_frame, textvariable=self.vars[key], width=30).grid(row=row_num, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=2)
            row_num += 1

        # --- Add Separator and Minimized Checkbox INSIDE env_frame ---
        ttk.Separator(env_frame, orient='horizontal').grid(row=row_num, column=0, columnspan=3, sticky='ew', pady=5) # Span 3 to cover button column too
        row_num += 1

        self.start_minimized_check = ttk.Checkbutton(
            env_frame,                                                                                         # Parent is env_frame
            text="Start minimized to tray on launch.",                                                         # Shortened text
            variable=self.start_minimized_var)
        self.start_minimized_check.grid(row=row_num, column=0, columnspan=3, sticky=tk.W, padx=5, pady=(5, 5)) # Span 3

        # Disable if tray icon is not available
        if not has_pystray:
            self.start_minimized_check.config(state=tk.DISABLED, text="Start minimized (Requires pystray)")

        # --- Buttons (Inside Left Panel) ---
        button_frame = ttk.Frame(left_panel_frame, padding="5")
        # Place below env_frame
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10) # No columnspan needed
                                                                         # Configure columns to distribute space EVENLY for buttons
        button_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.style = ttk.Style()
        self.style.configure('Start.TButton', background='#00aa00')
        self.style.configure('Stop.TButton', background='#aa0000')

        self.start_button = ttk.Button(button_frame, text="ollama run", command=self.start_ollama, style='Start.TButton')
        self.start_button.grid(row=0, column=0, padx=2, sticky='ew')

        self.stop_button = ttk.Button(button_frame, text="ollama stop", command=self.stop_ollama, style='Stop.TButton', state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=2, sticky='ew')

        self.copy_log_button = ttk.Button(button_frame, text="Copy Log", command=self.copy_log)
        self.copy_log_button.grid(row=0, column=2, padx=2, sticky='ew')

        self.clear_log_button_widget = ttk.Button(button_frame, text="Clear Log", command=self.clear_log)
        self.clear_log_button_widget.grid(row=0, column=3, padx=2, sticky='ew')

        self.hide_button = ttk.Button(button_frame, text="Hide to tray", command=self.hide_window)
        self.hide_button.grid(row=0, column=4, padx=2, sticky='ew')

        # --- Status Bar (Inside Left Panel) ---
        self.status_var = tk.StringVar(value="Status: Idle.")
        status_bar = ttk.Label(left_panel_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding="2")
        # Place below button_frame
        status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 0)) # No columnspan needed

        # --- Log Area (Inside Main Frame, Right Column) ---
        log_frame = ttk.LabelFrame(main_frame, text="Ollama Log Output", padding="5")
        # Place in main_frame's right column, spanning vertically if needed (though row 0 weight handles expansion)
        log_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=0) # Removed vertical pady
                                                                                 # Configure log_frame's internal grid
        log_frame.columnconfigure(0, weight=1)                                   # Text widget expands horizontally
        log_frame.rowconfigure(0, weight=1)                                      # Text widget expands vertically

        self.log_widget = AnsiColorText(log_frame, wrap=tk.NONE, width=80, height=25) # Added default size
        self.log_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbars targeting log_widget within log_frame
        h_scrollbar = ttk.Scrollbar(log_frame, orient=tk.HORIZONTAL, command=self.log_widget.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.log_widget.configure(xscrollcommand=h_scrollbar.set)

        v_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_widget.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_widget.configure(yscrollcommand=v_scrollbar.set)

        # --- Load Initial Settings & Start Log Processing ---
        self.load_settings()     # Load settings first
        self.process_log_queue() # Start checking the queue

        # --- 菜单栏 ---
        menubar = tk.Menu(root)

        # --- Application 菜单 ---
        app_menu = tk.Menu(menubar, tearoff=0)
        if has_pystray:
            app_menu.add_command(label="Hide to Tray", command=self.hide_window)
        app_menu.add_command(label="save Log", command=self.save_log_to_file)
        app_menu.add_separator()
        app_menu.add_command(label="Exit", command=self.on_closing)
        menubar.add_cascade(label="App", menu=app_menu) # 添加 Application 级联菜单

        # --- Help&About 菜单 ---
        help_about_menu = tk.Menu(menubar, tearoff=0)                  # 创建新的菜单对象
        help_about_menu.add_command(label="Help", command=self.help)   # 添加 Help 命令
        help_about_menu.add_command(label="About", command=self.about) # 添加 About 命令
        menubar.add_cascade(label="Info", menu=help_about_menu)        # 添加 Help&About 级联菜单

        root.config(menu=menubar) # 将修改后的菜单栏配置给主窗口

        # --- Check for Start Minimized (Keep this at the end of __init__) ---
        # Use after() to allow the window to initialize before hiding
        if has_pystray and self.start_minimized_var.get():
            self.root.after(100, self.hide_window) # Slightly longer delay

        self.app_info(WELCONE_TEXT)
        self.app_info("this is a ollama launcher info text demo.")
        self.app_warn("this is a ollama launcher warning text demo.")
        self.app_err("this is a ollama launcher error text demo.")
        self.log_time()

    # --- Methods (browse_*, load_settings, save_settings are the same) ---

    def help(self):
        help_page()

    def about(self):
        about_page()

    def setup_tray_icon(self):
        """Sets up the system tray icon and menu."""
        global has_pystray
        try:
            icon_bytes = base64.b64decode(icon_base64_data)
            icon_stream = io.BytesIO(icon_bytes)
            image = Image.open(icon_stream) # <--- 这是替换后的核心行

        except base64.binascii.Error:
            messagebox.showerror("Error", f"Failed to load icon : wrong base64 bmp code.")
            self.app_err(f"Failed to load icon : wrong base64 bmp code.")
            print(f"Failed to load icon : wrong base64 bmp code: {e}")
            has_pystray = False
            return

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load base64 bmp icon: {e}. Tray icon disabled.")
            self.app_err(f"Failed to load base64 bmp icon: {e}. Tray icon disabled.")
            print(f"Error loading icon: {e}")
            has_pystray = False
            return

        # Define menu items (text, callback function)
        # IMPORTANT: Callbacks need to be wrapped to run on the main Tkinter thread using root.after
        menu = pystray.Menu(
            pystray.MenuItem(
                'Show Launcher',
                lambda: self.root.after(0, self.show_window), # Schedule show_window
                default=True                                  # Default action on left-click
            ),
            pystray.MenuItem(
                'Start Ollama',
                lambda: self.root.after(0, self.start_ollama) # Schedule start_ollama
            ),
            pystray.MenuItem(
                'Stop Ollama',
                lambda: self.root.after(0, self.stop_ollama)  # Schedule stop_ollama
            ),
            pystray.MenuItem(
                'Exit',
                lambda: self.root.after(0, self.on_closing)   # Schedule on_closing()
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

    def load_settings(self):
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r') as f:
                    loaded_settings = json.load(f)
                self.settings = DEFAULT_SETTINGS.copy()
                self.settings.update({k: v for k, v in loaded_settings.items() if k != 'variables'})
                if 'variables' in loaded_settings:
                    self.settings['variables'].update(loaded_settings['variables'])
                self.status_var.set("Status: Settings loaded from config.json")
                self.app_info("Status: Settings loaded from config.json")
            else:
                self.settings = DEFAULT_SETTINGS.copy()
                self.status_var.set("Status: config.json not found. Using default settings.")
                self.app_warn("Status: config.json not found. Using default settings.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings: {e}")
            self.app_err(f"Failed to load settings: {e}")
            self.settings = DEFAULT_SETTINGS.copy()
            self.status_var.set("Status: Error loading settings. Using defaults.")
            self.app_err("Status: Error loading settings. Using defaults.")

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
            elif key != 'ollama_exe_path' and key not in self.settings['variables'] and key in DEFAULT_SETTINGS['variables']:
                # If key missing in config but exists in defaults, set default
                value = DEFAULT_SETTINGS['variables'][key]
                if isinstance(tk_var, tk.IntVar):
                    tk_var.set(int(value))
                else:
                    tk_var.set(str(value))

        # Update start_minimized var (handle potential missing key)
        start_min_value = self.settings.get('start_minimized', DEFAULT_SETTINGS['start_minimized'])
        self.start_minimized_var.set(bool(start_min_value))

        # Ensure checkbox state reflects tray availability
        if not has_pystray:
            self.start_minimized_var.set(False)
            if hasattr(self, 'start_minimized_check'): # Check if widget exists yet
                self.start_minimized_check.config(state=tk.DISABLED)
        self.log_time()

    def save_settings(self):
        current_settings = {'ollama_exe_path': self.vars['ollama_exe_path'].get(), 'variables': {}, 'start_minimized': self.start_minimized_var.get()}
        for key, tk_var in self.vars.items():
            if key != 'ollama_exe_path':
                current_settings['variables'][key] = str(tk_var.get())

        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(current_settings, f, indent=4)
            self.settings = current_settings
            self.status_var.set("Status: Settings saved to config.json")
            self.app_info("Settings saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            self.app_err(f"Failed to save settings: {e}")
            self.status_var.set("Status: Error saving settings.")
            self.app_err("Status: Error saving settings.")
        self.log_time()

    def clear_log(self):
        self.log_widget.config(state=tk.NORMAL)
        self.log_widget.delete('1.0', tk.END)
        self.log_widget.active_codes = {'0'}
        self.log_widget.config(state=tk.DISABLED) # Explicitly set back to DISABLED
        self.log_time()

    def copy_log(self):
        log_content = self.log_widget.get('1.0', tk.END)

        try:
            self.root.clipboard_append(log_content)
            self.app_info("copy log to clipboard.")

        except tk.TclError as e:
            messagebox.showerror("Error", f"Error when copy LOG to clipboard: {e}")
            self.app_err(f"Error when copy LOG to clipboard: {e}")
        self.log_time()

    def update_log(self, message):
        self.log_widget.write_ansi(message)

    def log_time(self):
        self.log_queue.put(datetime.now().strftime("\x1b[94m[app time]\x1b[0m\t%Y - %m - %d \t%H:%M:%S\n"))

    def app_info(self, message):
        self.log_queue.put('\x1b[92m[app info]\x1b[0m\t' + message + '\n')

    def app_warn(self, message):
        self.log_queue.put('\x1b[93m[app warn]\x1b[0m\t' + message + '\n')

    def app_err(self, message):
        self.log_queue.put('\x1b[91m[app err ]\x1b[0m\t' + message + '\n')

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
            self.app_err(f"Error reading {pipe_name}: {e}")
        finally:
            pipe.close()                 # Ensure pipe is closed when reading stops
            self.app_warn(f"{pipe_name} stream closed")

    def start_ollama(self):
        if self.is_running:
            messagebox.showwarning("Info", "Ollama is already running.")
            self.app_warn("Ollama is already running.")
            return

        ollama_path = self.vars['ollama_exe_path'].get()
        if not ollama_path or not os.path.exists(ollama_path):
            messagebox.showerror("Error", f"Ollama executable not found at: {ollama_path}\nPlease set the correct path and save settings.")
            self.app_err(f"Ollama executable not found at: {ollama_path}\nPlease set the correct path and save settings.")
            self.status_var.set("Status: Error - Ollama path invalid.")
            self.app_err("Status: Error - Ollama path invalid.")
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
            self.update_log("\n\n")
            self.app_info("Starting Ollama Server...")
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
            self.app_info(f"Status: Ollama server running (PID: {self.ollama_process.pid})")
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
            self.app_err(f"Failed to start Ollama: {e}")
            self.status_var.set(f"Status: Error starting Ollama - {e}")
            self.is_running = False
            self.ollama_process = None
            self.start_button.config(state=tk.NORMAL) # Re-enable start button on failure
        self.log_time()

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
            self.app_info(status_message)
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
            self.app_info("Status: Idle (Ollama was not running).")
            return

        self.status_var.set("Status: Stopping Ollama...")
        self.app_info("Sending stop signal to Ollama")
        self.root.update_idletasks()

        try:
            # Important: Check if process is still alive before terminating
            if self.ollama_process.poll() is None:
                self.ollama_process.terminate()
                try:
                    self.ollama_process.wait(timeout=3)     # Wait up to 3 seconds
                except subprocess.TimeoutExpired:
                    self.app_info("Ollama did not terminate gracefully, killing...")
                    if self.ollama_process.poll() is None:  # Check again before kill
                        self.ollama_process.kill()
                        self.ollama_process.wait(timeout=2) # Wait for kill confirmation

            # Final check after attempts to stop
            exit_code = self.ollama_process.poll()
            self.is_running = False
            self.ollama_process = None # Clear process object
            status_msg = f"Status: Ollama server stopped (Exit Code: {exit_code})." if exit_code is not None else "Status: Ollama stopped (Exit code unknown)."
            self.status_var.set(status_msg)
            self.app_info(status_msg)
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Error", f"Error stopping Ollama: {e}")
            self.app_err(f"Error stopping Ollama: {e}")
            self.status_var.set(f"Status: Error stopping Ollama - {e}")
            self.app_err(f"Error stopping Ollama: {e}")
            # Attempt to reset state even on error
            self.is_running = False
            self.ollama_process = None
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
        self.log_time()

    # hide_window method removed as requested by replacing button

    def on_closing(self):
        self.app_info("exit...")
        self.log_time()
        if self.tray_icon:
            self.tray_icon.stop()
            self.app_info("Tray icon stopped.")

        if self.is_running:
            self.app_info("save config...")
            self.save_settings()
            self.app_info("stop ollama.exe...")
            self.stop_ollama()
            time.sleep(1)
            self.app_info("stop ollama.exe ok")
            self.root.destroy()
        else:
            self.app_info("save config...")
            self.save_settings()
            self.root.destroy()

    def get_log_content(self) -> str:
        # "1.0" 表示第一行第0个字符 (开始)
        # "end-1c" 表示结束位置之前的那个字符 (获取所有实际输入的文本)
        try:
            content = self.log_widget.get("1.0", "end-1c")
            return content
        except tk.TclError as e:
            print(f"Error when get log from console: {e}")
            return ""

    def save_log_to_file(self):
        log_text = self.get_log_content()
        if not log_text:
            messagebox.showinfo("Note", "Empty log.")
            return

        # 1. 生成建议的默认文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"ollama_launcher_{timestamp}.log"

        # 2. 获取当前工作目录作为默认打开路径
        initial_directory = os.getcwd()

        # 3. 定义文件类型过滤器
        file_types = [('Log files', '*.log'), ('Text files', '*.txt'), ('All files', '*.*')]

        # 4. 调用 asksaveasfilename 打开文件保存对话框
        file_path = filedialog.asksaveasfilename(
            title="save log ...",                 # 对话框标题
            initialdir=initial_directory,         # 初始目录
            initialfile=default_filename,         # 默认文件名
            defaultextension=".log",              # 默认扩展名 (如果用户没输入)
            filetypes=file_types                  # 文件类型过滤器
        )

        # 5. 检查用户是否选择了文件路径 (如果用户取消，则返回空字符串 "")
        if not file_path:
            return # 用户取消，则退出函数

        # 6. 如果用户选择了路径，则尝试写入文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(log_text)
            self.app_info(f"log save to: {file_path}")
        except IOError as e:
            self.app_err(f"saving log : '{file_path}' : an IO error : {e}")
        except Exception as e:
            self.app_err(f"saving log : '{file_path}' : get error : {e}")


if __name__ == "__main__":
    print('run')
    root = tk.Tk()
    app = OllamaLauncherGUI(root)
    root.mainloop()
    print('ok')
