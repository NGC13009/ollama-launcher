# coding = utf-8 (Zh-CN / Simplified Chinese)
# Arch   = win32
#
# @File name:       ollama_launcher.py
# @brief:           ollama launcher 启动器主程序
#                       打包：在当前conda环境下运行
#                           ```
#                           # -w 不要命令行终端， -F打包为单个文件，-i指定图标
#                           conda activate py312
#                           pyinstaller -w .\ollama_launcher.py -i .\favicon.ico -y
#                           pyinstaller -w .\ollama_launcher.py -i .\favicon.ico -y --distpath C:\application\ollama  # 直接打包到某路径
#                           ```.
# @attention:
# @TODO:            None
# @Author:          NGC13009
# @History:         2025-05-03		Create

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import json
import os
import threading
import time
import queue
import pystray
from PIL import Image, ImageTk
import re
import webbrowser
import threading
from datetime import datetime
import base64
import io
import requests
from urllib.parse import urlparse, urlencode
from pathlib import Path
from typing import Optional, Callable
import platform
import binascii
import psutil

from OL_resource import *
from OL_source_ico import icon_base64_data
from utils import *

has_pystray = True

# 配置文件的存储路径
CONFIG_FILE = "ollama_launcher_config.json"
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, CONFIG_FILE)

# 默认配置
DEFAULT_SETTINGS = {
    "ollama_exe_path": "C:/application/ollama/OLLAMA_FILE/ollama.exe", # 文件路径
    "variables": {
        "OLLAMA_MODELS": "E:/LLM/ollama_models",                       # 路径
        "OLLAMA_TMPDIR": "E:/LLM/ollama_models/temp",                  # 路径
        "OLLAMA_HOST": "127.0.0.1:11434",                              # ip:port
        "OLLAMA_ORIGINS": "*",                                         # 域名
        "OLLAMA_CONTEXT_LENGTH": "2048",                               # 正整数
        "OLLAMA_KV_CACHE_TYPE": "f16",                                 # 可选类型: f16, q8_0, q4_0
        "OLLAMA_KEEP_ALIVE": "-1",                                     # 整数
        "OLLAMA_MAX_QUEUE": "512",                                     # 正整数
        "OLLAMA_NUM_PARALLEL": "1",                                    # 正整数
        "OLLAMA_MAX_LOADED_MODELS": "4",                               # 正整数
        "OLLAMA_ENABLE_CUDA": "1",                                     # 0或1
        "CUDA_VISIBLE_DEVICES": "0",                                   # 英文逗号分隔的正整数
        "OLLAMA_FLASH_ATTENTION": "1",                                 # 0或1
        "OLLAMA_USE_MLOCK": "1",                                       # 0或1
        "OLLAMA_MULTIUSER_CACHE": "0",                                 # 0或1
        "OLLAMA_INTEL_GPU": "0",                                       # 0或1
        "OLLAMA_DEBUG": "0",                                           # 0或1
    },
    "start_minimized": False,
    "user_env": {}                                                     # 字典，包含环境变量name和var
}


class OllamaLauncherGUI:

    # Ollama 更新检查 API 地址
    UPDATE_CHECK_URL_BASE = "https://ollama.com/api/update"
    # GitHub Release 下载 URL 模板
    GITHUB_DOWNLOAD_URL_TEMPLATE = "https://github.com/ollama/ollama/releases/download/{version_tag}/{filename}"
    OLLAMA_WEBPAGE = "https://ollama.com/"
    OLLAMA_MODEL_LIST = "https://ollama.com/search"

    def __init__(self, root: tk.Tk):
        global has_pystray # Ensure global is accessible
        self.user_env = dict()
        self.root = root
        self.bg_color = '#efefef'
        self.fg_color = '#1e1e1e'
        root.configure(bg=self.bg_color)

        self.root.title("Ollama Launcher")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        h, w = 1450, 905
        self.root.minsize(h, w)
        self.root.geometry(f"{h}x{w}")

        try:
            icon_bytes = base64.b64decode(icon_base64_data)
            icon_stream = io.BytesIO(icon_bytes)
            pillow_image = Image.open(icon_stream)
            tk_icon = ImageTk.PhotoImage(pillow_image)
            self.root.iconphoto(True, tk_icon)
            self.icon = pillow_image
        except:
            print("base64 pic read fault!")
            exit(-1)

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
        style = ttk.Style(root)
        style.theme_use('clam') # Or 'alt', 'default', 'classic'
        style.configure('.', background=self.bg_color, foreground=self.fg_color)

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
            if key in ["OLLAMA_ENABLE_CUDA", "OLLAMA_FLASH_ATTENTION", "OLLAMA_USE_MLOCK", "OLLAMA_DEBUG", "OLLAMA_MULTIUSER_CACHE", "OLLAMA_INTEL_GPU"]: # 是 bool
                try:
                    init_val = int(default_value)
                except (ValueError, TypeError):
                    init_val = 0
                self.vars[key] = tk.IntVar(value=init_val)
                ttk.Checkbutton(env_frame, variable=self.vars[key]).grid(row=row_num, column=1, columnspan=2, sticky=tk.W, padx=5, pady=2)
            elif key in ["OLLAMA_MODELS", "OLLAMA_TMPDIR"]:                                                                                               # 需要配置路径的
                self.vars[key] = tk.StringVar(value=default_value)
                entry_frame = ttk.Frame(env_frame)

                entry_frame.grid(row=row_num, column=1, columnspan=2, sticky=(tk.W, tk.E))
                entry_frame.columnconfigure(0, weight=1)

                ttk.Entry(entry_frame, textvariable=self.vars[key], width=30).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(5, 0))
                ttk.Button(entry_frame, text="/", command=lambda k=key: self.browse_directory(k), width=2).grid(row=0, column=1, padx=5)
            elif key in ["OLLAMA_CONTEXT_LENGTH", "OLLAMA_MAX_QUEUE", "OLLAMA_NUM_PARALLEL", "OLLAMA_MAX_LOADED_MODELS"]: # 数值
                try:
                    init_val = int(default_value)
                except (ValueError, TypeError):
                    init_val = 0
                self.vars[key] = tk.IntVar(value=init_val)
                vcmd = self.root.register(validate_spinbox)
                spinbox = ttk.Spinbox(env_frame, textvariable=self.vars[key], from_=0, to=1048576, width=28, validate="key", validatecommand=(vcmd, "%P"))
                spinbox.grid(row=row_num, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=2)

            elif key == "OLLAMA_KV_CACHE_TYPE": # --- 特定字符串选项 (String Choice) 使用下拉菜单 (Combobox) ---
                self.vars[key] = tk.StringVar(value=default_value)
                options = ["f16", "q8_0", "q4_0"]

                if default_value not in options:
                    self.vars[key].set(options[0])

                try:
                    style.theme_use('clam')
                except tk.TclError:
                    pass

                style.map("Custom.TCombobox",
                          fieldbackground=[('readonly', 'white')],
                          foreground=[('readonly', 'black')],
                          selectbackground=[('readonly', 'white')],
                          selectforeground=[('readonly', 'black')])

                combobox = ttk.Combobox(env_frame, textvariable=self.vars[key], values=options, state="readonly", width=28, style="Custom.TCombobox")
                combobox.grid(row=row_num, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=2)

            else:  # 其他就正常文本框
                self.vars[key] = tk.StringVar(value=default_value)
                ttk.Entry(env_frame, textvariable=self.vars[key], width=30).grid(row=row_num, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=2)
            row_num += 1

        # --- Add Separator and Minimized Checkbox INSIDE env_frame ---
        ttk.Separator(env_frame, orient='horizontal').grid(row=row_num, column=0, columnspan=3, sticky='ew', pady=5) # Span 3 to cover button column too
        row_num += 1

        self.start_minimized_check = ttk.Checkbutton(
            env_frame,                                                                                         # Parent is env_frame
            text="Auto start ollama & hide to tray on launch.",                                                # Shortened text
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
        self.style.configure('Start.TButton', background="#42d39b")
        self.style.configure('Stop.TButton', background="#fc7c7c")
        self.style.configure('Hide.TButton', background="#6ea8e6")

        self.start_button = ttk.Button(button_frame, text="Ollama Run", command=self.start_ollama, style='Start.TButton')
        self.start_button.grid(row=0, column=0, padx=2, sticky='ew')

        self.stop_button = ttk.Button(button_frame, text="Ollama Stop", command=self.stop_ollama, style='Stop.TButton', state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=2, sticky='ew')

        self.copy_log_button = ttk.Button(button_frame, text="Copy Log", command=self.copy_log)
        self.copy_log_button.grid(row=0, column=2, padx=2, sticky='ew')

        self.clear_log_button_widget = ttk.Button(button_frame, text="Clear Log", command=self.clear_log)
        self.clear_log_button_widget.grid(row=0, column=3, padx=2, sticky='ew')

        self.hide_button = ttk.Button(button_frame, text="Hide to tray", command=self.hide_window, style='Hide.TButton')
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
        self.log_widget.config(state=tk.NORMAL)          # 允许选中/复制
        self.log_widget.bind("<Key>", lambda e: "break") # 阻止用户输入
        self.log_widget.bind("<Control-c>", self.log_widget.copy_selection)

        # --- Load Initial Settings & Start Log Processing ---
        self.load_settings()     # Load settings first
        self.process_log_queue() # Start checking the queue

        # --- 菜单栏 ---
        menubar = tk.Menu(root)

        # --- Application 菜单 ---
        app_menu = tk.Menu(menubar, tearoff=0)
        if has_pystray:
            app_menu.add_command(label="Hide to Tray", command=self.hide_window)
        app_menu.add_command(label="Print Welcome", command=self.welcome_text)
        app_menu.add_separator()
        app_menu.add_command(label="Edit additional Environment", command=self.open_env_editor)
        app_menu.add_command(label="Save Config", command=self.save_settings)
        app_menu.add_command(label="Reset Config", command=self.reset_settings)
        app_menu.add_separator()
        app_menu.add_command(label="Exit", command=self.on_closing)
        menubar.add_cascade(label="App", menu=app_menu) # 添加 Application 级联菜单

        # --- action 菜单 ---
        action_menu = tk.Menu(menubar, tearoff=0)
        action_menu.add_command(label="▶ Ollama Run", command=self.start_ollama)
        action_menu.add_command(label="■ Ollama Stop", command=self.stop_ollama)
        menubar.add_cascade(label="Action", menu=action_menu)

        # --- log 菜单 ---
        log_menu = tk.Menu(menubar, tearoff=0)
        log_menu.add_command(label="Enable wrap", command=lambda: self.log_widget.configure(wrap=tk.WORD))
        log_menu.add_command(label="Disable wrap", command=lambda: self.log_widget.configure(wrap=tk.NONE))
        log_menu.add_separator()
        log_menu.add_command(label="Save Log", command=self.save_log_to_file)
        log_menu.add_command(label="Copy Log", command=self.copy_log)
        log_menu.add_separator()
        log_menu.add_command(label="Clear Log", command=self.clear_log)
        menubar.add_cascade(label="Log", menu=log_menu)

        # --- Help&About 菜单 ---
        help_about_menu = tk.Menu(menubar, tearoff=0)
        help_about_menu.add_command(label="Ollama webpage", command=self.ollama_webpage)
        help_about_menu.add_command(label="Ollama model list", command=self.ollama_model_list)
        help_about_menu.add_command(label="Download Ollama", command=self.get_update_url_msgbox)
        help_about_menu.add_command(label="Open Ollama path", command=self.open_ollama_path)
        help_about_menu.add_separator()
        help_about_menu.add_command(label="System info", command=self.get_platform_details_msgbox)
        help_about_menu.add_command(label="Ollama version", command=self.get_ollama_version_msgbox)
        help_about_menu.add_separator()
        help_about_menu.add_command(label="Help", command=self.help)
        help_about_menu.add_command(label="About", command=self.about)
        menubar.add_cascade(label="Info", menu=help_about_menu)

        root.config(menu=menubar) # 将修改后的菜单栏配置给主窗口

        # --- Check for Start Minimized (Keep this at the end of __init__) ---
        # Use after() to allow the window to initialize before hiding
        if has_pystray and self.start_minimized_var.get():
            self.start_ollama()
            self.root.after(100, self.hide_window) # Slightly longer delay
        self.welcome_text()

    def welcome_text(self):
        self.app_info("-+++-----------------------------------------------+++-")
        self.app_info(WELCONE_TEXT)
        self.app_info("this is a ollama launcher info text demo.")
        self.app_warn("this is a ollama launcher warning text demo.")
        self.app_err("this is a ollama launcher error text demo.")
        self.app_time()
        self.app_info("-+++-----------------------------------------------+++-")

    # --- Methods (browse_*, load_settings, save_settings are the same) ---

    def help(self):
        self.app_info("open Help Page.")
        help_window = tk.Toplevel()
        help_window.title("Help - Ollama Launcher")
        help_window.geometry("800x600")
        help_window.minsize(800, 600) # 设置最小大小
        tk_icon = ImageTk.PhotoImage(self.icon)
        help_window.iconphoto(True, tk_icon)

        help_window.configure(bg=self.bg_color)

        # 选项卡
        notebook = ttk.Notebook(help_window)
        notebook.pack(expand=True, fill='both')

        help_frame = dict()
        text_area = []
        la_list = []

        for lan, help_text in HELP_TEXT_DICT.items():

            help_frame[lan] = ttk.Frame(notebook)
            notebook.add(help_frame[lan], text=lan)

            # 内容区域
            text_cur = scrolledtext.ScrolledText(help_frame[lan], wrap=tk.WORD, width=80, height=20, bg=self.bg_color, fg=self.fg_color, bd=0, highlightthickness=0)
            text_cur.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)
            text_cur.insert(tk.END, help_text)
            text_cur.config(state=tk.DISABLED)

            # 允许用户选中和复制文本
            text_cur.tag_configure("selectable", selectforeground="black", selectbackground="lightgray")
            text_cur.tag_add("selectable", "1.0", tk.END)

            text_area.append(text_cur)
            la_list.append(lan)

        style = ttk.Style()
        style.configure("HelpButtonFrame.TFrame", background=self.bg_color)
        button_frame = ttk.Frame(help_window, style="HelpButtonFrame.TFrame")
        button_frame.pack(pady=10)

        copy_help = ttk.Button(button_frame, text="copy to clip board", command=lambda: self.copy_help(notebook, la_list))
        copy_help.pack(side=tk.LEFT, padx=5)
        ok_button = ttk.Button(button_frame, text="Open help in webpage", command=self.open_git_webpage)
        ok_button.pack(side=tk.LEFT, padx=5)
        close_button = ttk.Button(button_frame, text="X", command=help_window.destroy)
        close_button.pack(side=tk.LEFT, padx=5)

        help_window.update_idletasks()
        width = help_window.winfo_width()
        height = help_window.winfo_height()
        x = (help_window.winfo_screenwidth() // 2) - (width // 2)
        y = (help_window.winfo_screenheight() // 2) - (height // 2)
        help_window.geometry(f"{width}x{height}+{x}+{y}")

    def copy_help(self, notebook, la_list):
        try:
            current_tab = notebook.select()         # 获取当前选项卡
            tab_index = notebook.index(current_tab) # 获取选项卡索引
            lan = la_list[tab_index]
            self.root.clipboard_clear()
            self.root.clipboard_append(HELP_TEXT_DICT[lan])
            self.app_time('copy help document to clipboard.')
            messagebox.showinfo("Note", "Copy help document to clipboard success.")

        except tk.TclError as e:
            messagebox.showerror("Error", f"Error when copy help document to clipboard: {e}")
            self.app_err(f"Error when copy help document to clipboard: {e}")

    def about(self):
        self.app_info("open About Page.")
        about_window = tk.Toplevel()
        about_window.title("About - Ollama Launcher")
        about_window.geometry("500x250")
        about_window.resizable(False, False)
        tk_icon = ImageTk.PhotoImage(self.icon)
        about_window.iconphoto(True, tk_icon)

        about_window.configure(bg=self.bg_color)

        style = ttk.Style()
        style.configure("About.TFrame", background=self.bg_color)
        style.configure("About.TLabel", background=self.bg_color, foreground=self.fg_color)

        container = ttk.Frame(about_window, style="About.TFrame")
        container.pack(expand=True, fill="both", padx=10, pady=10)

        label = ttk.Label(container, text=INFO_TEXT, justify="center", style="About.TLabel")
        label.pack(pady=10)

        style = ttk.Style()
        style.configure("About.TButton")
        github_button = ttk.Button(container, text=GITLINK_BOTTOM, style="About.TButton", command=self.open_git_webpage)
        github_button.pack()

    def setup_tray_icon(self):
        """Sets up the system tray icon and menu."""
        global has_pystray

        # Define menu items (text, callback function)
        # IMPORTANT: Callbacks need to be wrapped to run on the main Tkinter thread using root.after
        menu = pystray.Menu(
            pystray.MenuItem(
                'Show Launcher',
                lambda: self.root.after(0, self.show_window), # Schedule show_window
                default=True                                  # Default action on left-click
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                '▶ Ollama Run',
                lambda: self.root.after(0, self.start_ollama) # Schedule start_ollama
            ),
            pystray.MenuItem(
                '■ Ollama Stop',
                lambda: self.root.after(0, self.stop_ollama)  # Schedule stop_ollama
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                'Exit',
                lambda: self.root.after(0, self.on_closing)   # Schedule on_closing()
            ))

        # Create the icon object
        self.tray_icon = pystray.Icon("OllamaLauncher", self.icon, "Ollama Launcher", menu)

    def start_tray_thread(self):
        """Runs the pystray icon in a separate thread."""
        if self.tray_icon:
            # Run the icon loop in a daemon thread so it exits when the main app exits
            tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            tray_thread.start()
        else:
            self.app_err("Cannot start tray thread: tray icon not set up.")

    def hide_window(self):
        self.app_time("Hide the Ollama Launcher main Window to tray.")
        self.root.withdraw()

        # 我觉得还是算了，不要每次最小化都弹出提示
        # if self.tray_icon and self.tray_icon.HAS_NOTIFICATION:
        #     self.tray_icon.notify("Ollama Launcher hidden to tray.")

    def show_window(self):
        self.app_time("Shows the Ollama Launcher main Window from hidden state.")
        self.root.deiconify()
        self.root.lift()        # Bring window to front
        self.root.focus_force() # Force focus

    def browse_ollama_exe(self):
        path = filedialog.askopenfilename(title="Select ollama.exe", filetypes=(("Executable files", "*.exe"), ("All files", "*.*")))
        if path:
            self.vars['ollama_exe_path'].set(path)
            self.app_info(f"set the ollama_exe_path = '{path}'")

    def browse_directory(self, key):
        path = filedialog.askdirectory(title=f"Select Directory for {key}", initialdir=self.vars[key].get() or SCRIPT_DIR)
        if path:
            self.vars[key].set(path)
            self.app_info(f"set the '{key}' = '{path}'")

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

        self.enable_settings()

    def reset_settings(self):
        current_settings = DEFAULT_SETTINGS

        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(current_settings, f, indent=4)
            self.settings = current_settings
            self.status_var.set("Status: Reset Settings & saved to config.json")
            self.app_info("Reset Settings & saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e} in reset_setting function.")
            self.app_err(f"Failed to save settings: {e} in reset_setting function.")
            self.status_var.set("Status: Error saving settings in reset_setting function.")
        self.enable_settings()

    def enable_settings(self):
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

        error_code = self.check_settings()
        if error_code > 0:
            self.app_err(f'Project setup check failed. Can not enable settings. Error with {bin(error_code)}')
            self.app_time()
            return

        # Update start_minimized var (handle potential missing key)
        start_min_value = self.settings.get('start_minimized', DEFAULT_SETTINGS['start_minimized'])
        self.start_minimized_var.set(bool(start_min_value))
        self.user_env = self.settings.get('user_env', DEFAULT_SETTINGS['user_env'])

        # Ensure checkbox state reflects tray availability
        if not has_pystray:
            self.start_minimized_var.set(False)
            if hasattr(self, 'start_minimized_check'): # Check if widget exists yet
                self.start_minimized_check.config(state=tk.DISABLED)
        self.app_time('settings enabled.')

    def save_settings(self):
        error_code = self.check_settings()
        if error_code > 0:
            self.app_err(f'Project setup check failed. No new configurations will be stored until it is fixed. Error with {bin(error_code)}')
            self.app_time()
            return
        current_settings = {'ollama_exe_path': self.vars['ollama_exe_path'].get(), 'variables': {}, 'start_minimized': self.start_minimized_var.get(), "user_env": self.user_env}
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
        self.app_time('settings saved.')

    def clear_log(self):
        self.log_widget.delete('1.0', tk.END)
        self.log_widget.active_codes = {'0'}
        self.app_time()

    def copy_log(self):
        log_content = self.log_widget.get('1.0', tk.END)

        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(log_content)

        except tk.TclError as e:
            messagebox.showerror("Error", f"Error when copy LOG to clipboard: {e}")
            self.app_err(f"Error when copy LOG to clipboard: {e}")
        self.app_time('copy log to clipboard.')

    def update_log(self, message):
        message = colorize_gin_log(message)
        self.log_widget.write_ansi(message)
        print(message, end='', flush=True)

    def app_time(self, text=''):
        self.log_queue.put('\x1b[94m[app time]\t' + self.get_str_time() + '\t--- ' + text + '\x1b[0m\n')

    def get_str_time(self):
        text = datetime.now().strftime("%Y - %m - %d \t%H:%M:%S")
        return text

    def app_info(self, message):
        self.log_queue.put('\x1b[92m[app info]\x1b[0m\t' + message + '\n')

    def app_warn(self, message):
        self.log_queue.put('\x1b[93m[app warn]\t' + message + '\x1b[0m\n')

    def app_err(self, message):
        self.log_queue.put('\x1b[91m[app  err]\t' + message + '\x1b[0m\n')

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
            self.app_info(f"{pipe_name} stream closed")

    def start_ollama(self):
        error_code = self.check_settings()
        if error_code > 0:
            self.app_err(f'Project setup check failed. Ollama not start. Error with {bin(error_code)}')
            self.app_time()
            return

        if self.is_running:
            messagebox.showwarning("Info", "Ollama is already running.")
            self.app_warn("Ollama is already running.")
            return

        ollama_path = self.vars['ollama_exe_path'].get()
        if not ollama_path or not os.path.exists(ollama_path):
            messagebox.showerror("Error", f"Ollama executable not found at: {ollama_path}\nPlease set the correct path and save settings.")
            self.app_err(f"Ollama executable not found at: {ollama_path}\nPlease set the correct path and save settings.")
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

        env.update(self.user_env) # marge user_env into the environment variables

        self.app_info(f"ENV: {env}")
        self.app_info(f"ollama_dir: {ollama_dir}")

        try:
            self.status_var.set("Status: Starting Ollama...")
            self.update_log("\n\n")
            self.app_info("Starting Ollama Server...")
            self.root.update_idletasks()

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
                creationflags=subprocess.CREATE_NO_WINDOW)

            self.is_running = True
            self.status_var.set(f"Status: Ollama server running (PID: {self.ollama_process.pid})")
            self.app_info(f"Status: Ollama server running (PID: {self.ollama_process.pid})")
            ddd = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.tray_icon.notify(f"Ollama Server started. PID: {self.ollama_process.pid}\nTime : {ddd}")
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
        self.app_time('ollama server started.')

    def monitor_process_exit(self):
        """Waits for process exit and schedules GUI update."""
        exit_code = self.ollama_process.wait()
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
    def psutil_terminate(self, proc_pid):
        parent_proc = psutil.Process(proc_pid)
        for child_proc in parent_proc.children(recursive=True):
            self.app_info(f"terminate proc PID: {child_proc.ppid()} ...")
            child_proc.terminate()
        parent_proc.terminate()

    def stop_ollama(self):
        if not self.is_running or not self.ollama_process:
            self.is_running = False # Ensure state consistency
            self.ollama_process = None
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_var.set("Status: Idle (Ollama was not running).")
            self.app_warn("Ollama was not running.")
            messagebox.showinfo("Note", f"Ollama was not running.")
            return

        self.status_var.set("Status: Stopping Ollama...")
        self.app_info("Sending stop signal to Ollama")
        self.root.update_idletasks()

        try:
            # Important: Check if process is still alive before terminating
            if self.ollama_process.poll() is None:
                self.psutil_terminate(self.ollama_process.pid)
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
            status_msg = f"Status: Ollama server stopped (Exit Code: {exit_code})."
            self.status_var.set(status_msg)
            self.app_info(status_msg)
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            ddd = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.tray_icon.notify(f"Ollama Server stopped with code : {exit_code}\nTime : {ddd}")
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
        self.app_time('ollama server stoped.')

    # hide_window method removed as requested by replacing button

    def on_closing(self):
        self.app_info('exit...')
        self.app_time()
        if self.is_running:
            result = messagebox.askyesnocancel("Note",
                                               "Do you really want to EXIT?",
                                               detail="Ollama server is running.\nIf you want to stop ollama deamon & exit, choose Yes.\nIf you want to hidden the window to tray, choose NO.",
                                               icon=messagebox.WARNING,
                                               default=messagebox.CANCEL)
            if result == True:
                self.app_info("stop ollama.exe...")
                self.stop_ollama()

                if self.tray_icon:
                    self.app_info("stop tray icon...")
                    self.root.after(950, self.tray_icon.stop) # 必须小于self.root.destroy()的触发时间

                self.app_info("save config...")
                self.save_settings()
                self.app_warn("OK. Will exit after 1 second...")
                self.root.after(1000, self.root.destroy)
            elif result == False:
                self.hide_window()
                return
            else:  # return None
                return

        else:
            if self.tray_icon:
                self.app_info("stop tray icon...")
                self.tray_icon.stop()

            self.app_info("save config...")
            self.save_settings()
            self.app_warn("OK. Will exit...")
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

    def open_env_editor(self):
        # --- Create the Toplevel window ---
        editor_window = tk.Toplevel(self.root)
        editor_window.title("Additional Environment Variable Editor")
        editor_window.geometry("450x400")
        editor_window.minsize(450, 400)
        editor_window.maxsize(450, 8192)

        # --- Data Storage ---
        # List to keep track of row widgets (frame, key_entry, value_entry)
        # This makes adding/removing rows and getting values easier
        row_widgets = []

        # --- Main Frames ---
        # Frame to hold the scrollable entry rows
        header_frame = tk.Frame(editor_window)
        header_frame.pack(pady=(5, 0), padx=10, fill=tk.X)

        # Use a Canvas and Frame for scrolling if many entries are expected
        canvas_frame = tk.Frame(editor_window)
        canvas_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(canvas_frame)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        # Use Frame from ttk if you imported it for better theme consistency
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Frame for control buttons
        button_frame = tk.Frame(editor_window)
        button_frame.pack(pady=(5, 10), padx=10, fill=tk.X)

        # --- Headers ---
        tk.Label(header_frame, text="Key").pack(side=tk.LEFT, padx=(5, 0), expand=True, anchor='w')
        tk.Label(header_frame, text="Value").pack(side=tk.LEFT, padx=(5, 50), expand=True, anchor='w') # Extra padding to align roughly

        # --- Functions for Row Management ---
        def add_row(key="", value=""):
            """Adds a new row with key/value entries to the scrollable_frame."""
            row_frame = tk.Frame(scrollable_frame)
            row_frame.pack(fill=tk.X, pady=2)

            key_entry = tk.Entry(row_frame, width=25)
            key_entry.pack(side=tk.LEFT, padx=(0, 5), expand=True, fill=tk.X)
            key_entry.insert(0, key)

            value_entry = tk.Entry(row_frame, width=25)
            value_entry.pack(side=tk.LEFT, padx=(0, 5), expand=True, fill=tk.X)
            value_entry.insert(0, value)

            # Simple remove button per row (alternative to "remove last")
            remove_button = tk.Button(row_frame, text="-", command=lambda: remove_specific_row(row_frame, row_widgets))
            remove_button.pack(side=tk.LEFT, padx=(5, 0))

            # Store references
            row_info = {"frame": row_frame, "key": key_entry, "value": value_entry, "remove_btn": remove_button}
            row_widgets.append(row_info)
            update_remove_buttons_state() # Enable/disable remove buttons

        def remove_specific_row(row_frame_to_remove, row_widgets):
            """Removes the specific row associated with the button pressed."""
            # Find the index of the row to remove
            index_to_remove = -1
            for i, row_info in enumerate(row_widgets):
                if row_info["frame"] == row_frame_to_remove:
                    index_to_remove = i
                    break

            # Destroy widgets
            row_widgets[index_to_remove]["frame"].destroy()
            # Remove from list
            del row_widgets[index_to_remove]
            update_remove_buttons_state() # Update button states after removal

        def update_remove_buttons_state():
            for row_info in row_widgets:
                # Check if button still exists before configuring
                if row_info["remove_btn"].winfo_exists():
                    row_info["remove_btn"].config(state=tk.NORMAL)

        # --- Function to Save and Close ---
        def save_and_close():
            """Collects data from entries, updates self.user_env, and closes."""
            new_env = {}
            for row_info in row_widgets:
                key = row_info["key"].get().strip()
                value = row_info["value"].get().strip()
                if key: # Only add if key is not empty
                    new_env[key] = value

            # Update the parent's attribute
            self.user_env = new_env
            editor_window.destroy() # Close the Toplevel window

        # --- Create Control Buttons ---
        add_button = tk.Button(button_frame, text="   +   ", command=add_row)
        add_button.pack(side=tk.LEFT, padx=5)

        save_button = tk.Button(button_frame, text="   OK   ", command=save_and_close) # Highlight save
        save_button.pack(side=tk.RIGHT, padx=5)

        # --- Populate Initial Rows ---
        if len(self.user_env) == 0:
            add_row()
        for k, v in self.user_env.items():
            add_row(k, v)

        # --- Handle Window Close Button (X) ---
        # Make the 'X' button also trigger the save action
        editor_window.protocol("WM_DELETE_WINDOW", save_and_close)

        # --- Final Setup ---
        update_remove_buttons_state()        # Set initial state of remove buttons
        editor_window.transient(self.root)   # Keep the editor window on top of the main window
        editor_window.grab_set()             # Make the editor window modal (prevents interaction with main window)
        self.root.wait_window(editor_window) # Wait until the editor window is closed
        self.app_info(f"Updated self.user_env: {self.user_env}")

    def open_git_webpage(self):
        webbrowser.open_new(GITLINK)
        self.app_info("open webpage of ollama-launcher")

    def get_platform_details(self):
        system = platform.system().lower()
        arch = platform.machine().lower()

        # --- 架构映射 (根据 Go runtime 常量调整) ---
        arch_map = {
            'x86_64': 'amd64',
            'amd64': 'amd64',
            'arm64': 'arm64',
            'aarch64': 'arm64',
        }
        mapped_arch = arch_map.get(arch, arch)

        # --- 操作系统映射 ---
        os_map = {
            'darwin': 'darwin',   # macOS
            'linux': 'linux',
            'windows': 'windows',
        }
        mapped_os = os_map.get(system, system)
        self.app_info(f"system platfrom: os={mapped_os}, arch={mapped_arch}")
        return {"os": mapped_os, "arch": mapped_arch}

    def get_platform_details_msgbox(self):
        a = self.get_platform_details()
        ollama_version = self.get_ollama_version()
        os = a["os"]
        arch = a["arch"]
        messagebox.showinfo("System platfrom", f"os={a}\narch={arch}\nollama={ollama_version}")

    def get_ollama_platform_archive_url(self, current_version="0.0.0") -> Optional[str]:
        self.app_info(f"UPDATE_CHECK_URL_BASE: {self.UPDATE_CHECK_URL_BASE}")
        platform_info = self.get_platform_details()
        os_name = platform_info["os"]
        arch_name = platform_info["arch"]

        query_params = {
            "os": os_name,
            "arch": arch_name,
            "version": current_version,
            "ts": int(time.time()),
            "nonce": binascii.hexlify(os.urandom(16)).decode('utf-8'),
        }

        request_url = f"{self.UPDATE_CHECK_URL_BASE}?{urlencode(query_params)}"
        self.app_info(f"Ollama API: {request_url}")

        headers = {
            "User-Agent": f"python-ollama-checker/0.2 ({arch_name} {os_name}) Python/{platform.python_version()}",
        }
        self.app_info(f"Headers: {headers}")

        try:
            response = requests.get(request_url, headers=headers, timeout=15)

            if response.status_code == 204:
                self.app_info("Check update: This is the latest version. Don't need to update.")
                return None
            elif response.status_code == 200:
                self.app_info("url GET 200 OK")
                try:
                    update_data = response.json()
                    initial_url = update_data.get("url")

                    if not initial_url:
                        self.app_warn("The update respone lost value: URL. Update terminate.")
                        return None
                    self.app_info(f"API return URL: {initial_url}")

                    # --- 第二步：从 initial_url 提取版本标签 ---
                    version_tag = None
                    try:
                        path_parts = Path(urlparse(initial_url).path).parts
                        # 查找路径中 'vX.Y.Z' 格式的部分
                        for part in path_parts:
                            if part.startswith('v') and '.' in part and part.count('.') >= 2:
                                # 基本检查，确保至少有两个点
                                is_version = True
                                # 检查 v 后面的部分是否主要是数字和点
                                for char in part[1:]:
                                    if not (char.isdigit() or char == '.'):
                                        is_version = False
                                        break
                                if is_version:
                                    version_tag = part
                                    self.app_info(f"The version tag: {version_tag}")
                                    break
                        if not version_tag:
                            self.app_err("Can not get a valid version tag. Update terminate.")
                            return None
                    except Exception as e:
                        self.app_err(f"Error parsing URL to extract version tag: {e}. Update terminate.")
                        return None

                    # --- 第三步：根据平台确定目标文件名 ---
                    target_filename = None
                    if os_name == "windows":
                        target_filename = f"ollama-windows-{arch_name}.zip"
                    elif os_name == "linux":
                        # 根据用户提供的列表，Linux 使用 .tgz
                        target_filename = f"ollama-linux-{arch_name}.tgz"
                    elif os_name == "darwin":
                        # 根据用户提供的列表，macOS 使用统一的 .zip 文件名
                        target_filename = "Ollama-darwin.zip"
                    else:
                        self.app_err(f"Unsupported operating system for building file names: {os_name}. Update terminate.")
                        return None

                    if not target_filename:
                        self.app_err("Failed to determine the target file name. Update terminate.")
                        return None
                    self.app_info(f"Based on the target file name determined by the platform: {target_filename}")

                    # --- 第四步：构建最终的 GitHub 下载 URL ---
                    final_download_url = self.GITHUB_DOWNLOAD_URL_TEMPLATE.format(version_tag=version_tag, filename=target_filename)
                    self.app_info(f"Final download URL: {final_download_url}")
                    return (final_download_url, version_tag) # 返回构建好的 URL 字符串

                except requests.exceptions.JSONDecodeError:
                    self.app_err("Unable to parse the JSON content of the server response. Update terminate.")
                    return None
                except Exception as e:
                    self.app_err(f"Unknown error occurred while processing update response or building URL: {e}. Update terminate.")
                    return None

            elif response.status_code in [401, 403]:
                self.app_err(f"API fault with code: {response.status_code}.")
                self.app_err(f"respond: {response.text[:500]}... Update terminate.")
                return None
            else:
                self.app_warn(f"API fault with code: {response.status_code}")
                self.app_warn(f"respond: {response.text[:500]}... Update terminate.")
                return None

        except requests.exceptions.RequestException as e:
            self.app_err(f"Net error: {e}. Update terminate.")
            return None
        except Exception as e:
            self.app_err(f"Unknow error: {e}. Update terminate.")
            return None

    def get_update_url_msgbox(self):
        ret = self.get_ollama_platform_archive_url()
        if ret is None:
            self.app_err("Error occurred while processing update response or building URL. Update terminate.")
            return
        url, version_tag = ret
        ollama_version = self.get_ollama_version()

        if messagebox.askyesno("Ollama download",
                               f"The latest ollama version is {version_tag}. \nCurrent Version is {ollama_version}.\nWould you want to open web browser to download it?\nURL: {url}"):
            self.app_info("Ollama update: open the URL in web browser.")
            webbrowser.open_new(url)
        else:
            self.app_info("Ollama update: cancel open the download URL.")

    def ollama_webpage(self):
        webbrowser.open_new(self.OLLAMA_WEBPAGE)
        self.app_info("open webpage of OLLAMA_WEBPAGE")

    def ollama_model_list(self):
        webbrowser.open_new(self.OLLAMA_MODEL_LIST)
        self.app_info("open webpage of OLLAMA_MODEL_LIST")

    def get_ollama_version(self) -> str | None:
        error_code = self.check_settings()
        if error_code > 0:
            self.app_err(f'Project setup check failed. Fix problem and then to try again. Error with {bin(error_code)}')
            self.app_time()
            return

        ollama_path = self.vars['ollama_exe_path'].get()

        try:
            command = [ollama_path, "-v"]
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')

            output = result.stdout.strip()

            match = re.search(r"(?:ollama version is|client version is)\s+([\d\.]+)", output)

            if match:
                version = match.group(1)
                self.app_info(f"Ollama version tag: '{version}'")
                return version
            else:
                self.app_err(f"Can not get the version tag from stdout. Output was: '{output}'")
                return None

        except FileNotFoundError:
            self.app_err(f"Ollama executable was not found at path: '{ollama_path}'")
            return None
        except subprocess.CalledProcessError as e:
            self.app_err(f"Failed to run command '{' '.join(command)}'. Return code: {e.returncode}")
            if e.stdout:
                self.app_err(f"stdout: {e.stdout.strip()}")
            if e.stderr:
                self.app_err(f"stderr: {e.stderr.strip()}")
            return None
        except Exception as e:
            self.app_err(f"An unknown error occurred: {e}")
            return None

    def get_ollama_version_msgbox(self) -> str | None:
        version = self.get_ollama_version()
        if version is None:
            self.app_err(f"Error. Can not get the version tag.")
            return
        else:
            messagebox.showinfo("Ollama Version", f"The version of Ollama is: {version}")
            return

    def open_ollama_path(self):
        file_path_str = self.vars['ollama_exe_path'].get()
        try:
            directory_path = os.path.dirname(file_path_str) # 获取文件所在的目录

            if not directory_path:
                if os.path.isdir(file_path_str):
                    directory_path = file_path_str
                else:
                    self.app_err(f"Can not get the correct file path from : '{file_path_str}' ") # 输出错误提示
                    return

            # 3. 检查提取的目录路径是否存在
            if not os.path.exists(directory_path):                    # 检查目录是否存在
                self.app_err(f"path not exist : '{directory_path}' ") # 输出错误提示
                return

            if not os.path.isdir(directory_path): # 确保它确实是一个目录
                self.app_err(f"Path is not valid : '{directory_path}' ")
                return

            self.app_info(f"Open path : {directory_path}") # 打印将要打开的目录

            # 4. 根据操作系统类型打开目录
            current_os = platform.system() # 获取当前操作系统名称

            if current_os == "Windows":
                # 在Windows上，os.startfile() 可以直接打开目录（在文件浏览器中）
                os.startfile(os.path.normpath(directory_path))                            # 使用 normpath 确保路径格式正确
            elif current_os == "Darwin":                                                  # "Darwin" 是 macOS 的内核名称
                                                                                          # 在macOS上，使用 'open' 命令
                subprocess.run(['open', directory_path], check=True)                      # 执行 open 命令
            else:                                                                         # 默认为 Linux 或其他类 Unix 系统
                                                                                          # 在Linux上，通常使用 'xdg-open'
                try:
                    subprocess.run(['xdg-open', directory_path], check=True)              # 执行 xdg-open 命令
                except FileNotFoundError:                                                 # 如果 'xdg-open' 命令未找到
                    self.app_err(f"Detected OS = Linux. But can not find 'xdg-open'")     # 输出错误信息
                    self.app_err(f"Please open it manully: {directory_path}")             # 提示手动打开
                except subprocess.CalledProcessError as e:                                # 如果命令执行出错
                    self.app_err(f"Error occure when open '{directory_path}' with : {e}") # 输出错误信息

        except Exception as e:                  # 捕获其他所有可能的异常
            self.app_err(f"Unknow error : {e}") # 输出通用错误信息

    def check_settings(self, vars=None):
        error_code = 0
        if vars == None:
            vars = self.vars
        try:
            ollama_exe_path = vars['ollama_exe_path'].get()
            OLLAMA_MODELS = vars['OLLAMA_MODELS'].get()
            OLLAMA_TMPDIR = vars['OLLAMA_TMPDIR'].get()
            OLLAMA_HOST = vars['OLLAMA_HOST'].get()
            OLLAMA_ORIGINS = vars['OLLAMA_ORIGINS'].get()
            OLLAMA_CONTEXT_LENGTH = vars['OLLAMA_CONTEXT_LENGTH'].get()
            OLLAMA_KV_CACHE_TYPE = vars['OLLAMA_KV_CACHE_TYPE'].get()
            OLLAMA_KEEP_ALIVE = vars['OLLAMA_KEEP_ALIVE'].get()
            OLLAMA_MAX_QUEUE = vars['OLLAMA_MAX_QUEUE'].get()
            OLLAMA_NUM_PARALLEL = vars['OLLAMA_NUM_PARALLEL'].get()
            OLLAMA_MAX_LOADED_MODELS = vars['OLLAMA_MAX_LOADED_MODELS'].get()
            OLLAMA_ENABLE_CUDA = vars['OLLAMA_ENABLE_CUDA'].get()
            CUDA_VISIBLE_DEVICES = vars['CUDA_VISIBLE_DEVICES'].get()
            OLLAMA_FLASH_ATTENTION = vars['OLLAMA_FLASH_ATTENTION'].get()
            OLLAMA_USE_MLOCK = vars['OLLAMA_USE_MLOCK'].get()
            OLLAMA_MULTIUSER_CACHE = vars['OLLAMA_MULTIUSER_CACHE'].get()
            OLLAMA_INTEL_GPU = vars['OLLAMA_INTEL_GPU'].get()
            OLLAMA_DEBUG = vars['OLLAMA_DEBUG'].get()
        except Exception as e:
            self.app_err(f"Check fault! Error somewhere when loading config variables: {e}")
            messagebox.showerror("Check fault!", f"Error somewhere when loading config variables: {e}")
            error_code = 131072
            return error_code

        # Validate ollama_exe_path
        if (not ollama_exe_path) or (not os.path.isfile(ollama_exe_path)):
            self.app_err(f"Config fault! ollama_exe_path file not found: {ollama_exe_path}.")
            messagebox.showerror("Config fault!", f"ollama_exe_path file not found: {ollama_exe_path}")
            error_code += 1
        # Validate OLLAMA_MODELS
        if (not OLLAMA_MODELS) or (not os.path.isdir(OLLAMA_MODELS)):
            self.app_err(f"Config fault! OLLAMA_MODELS directory not found: {OLLAMA_MODELS}.")
            messagebox.showerror("Config fault!", f"OLLAMA_MODELS directory not found: {OLLAMA_MODELS}")
            error_code += 2

        # Validate OLLAMA_TMPDIR
        if (not OLLAMA_TMPDIR) or (not os.path.isdir(OLLAMA_TMPDIR)):
            self.app_err(f"Config fault! OLLAMA_TMPDIR directory not found: {OLLAMA_TMPDIR}.")
            messagebox.showerror("Config fault!", f"OLLAMA_TMPDIR directory not found: {OLLAMA_TMPDIR}")
            error_code += 4

        # Validate OLLAMA_HOST
        if not is_valid_host_port(OLLAMA_HOST):
            self.app_err(f"Config fault! OLLAMA_HOST must be a valid IP:port. Current value: {OLLAMA_HOST}")
            messagebox.showerror("Config fault!", "OLLAMA_HOST must be a valid IP:port")
            error_code += 8

        # Validate OLLAMA_ORIGINS
        # it just any string...

        # Validate OLLAMA_CONTEXT_LENGTH
        if OLLAMA_CONTEXT_LENGTH <= 0:
            self.app_err("fConfig fault! OLLAMA_CONTEXT_LENGTH must be a positive integer. Current value: {OLLAMA_CONTEXT_LENGTH}")
            messagebox.showerror("Config fault!", "OLLAMA_CONTEXT_LENGTH must be a positive integer")
            error_code += 16

        # Validate OLLAMA_KV_CACHE_TYPE
        if OLLAMA_KV_CACHE_TYPE not in ["f16", "q8_0", "q4_0"]:
            self.app_err(f"Config fault! OLLAMA_KV_CACHE_TYPE must be one of 'f16', 'q8_0', 'q4_0'. Current value: {OLLAMA_KV_CACHE_TYPE}")
            messagebox.showerror("Config fault!", "OLLAMA_KV_CACHE_TYPE must be one of 'f16', 'q8_0', 'q4_0'")
            error_code += 32

        # OLLAMA_KEEP_ALIVE can be "1500" or such as "5m0s"... 不弄了算了

        # Validate OLLAMA_MAX_QUEUE
        if OLLAMA_MAX_QUEUE <= 0:
            self.app_err(f"Config fault! OLLAMA_MAX_QUEUE must be a positive integer. Current value: {OLLAMA_MAX_QUEUE}")
            messagebox.showerror("Config fault!", "OLLAMA_MAX_QUEUE must be a positive integer")
            error_code += 128

        # Validate OLLAMA_NUM_PARALLEL
        if int(OLLAMA_NUM_PARALLEL) <= 0:
            self.app_err(f"Config fault! OLLAMA_NUM_PARALLEL must be a positive integer. Current value: {OLLAMA_NUM_PARALLEL}")
            messagebox.showerror("Config fault!", "OLLAMA_NUM_PARALLEL must be a positive integer")
            error_code += 256

        # Validate OLLAMA_MAX_LOADED_MODELS
        if OLLAMA_MAX_LOADED_MODELS <= 0:
            self.app_err(f"Config fault! OLLAMA_MAX_LOADED_MODELS must be a positive integer. Current value: {OLLAMA_MAX_LOADED_MODELS}")
            messagebox.showerror("Config fault!", "OLLAMA_MAX_LOADED_MODELS must be a positive integer")
            error_code += 512

        # Validate CUDA_VISIBLE_DEVICES
        if CUDA_VISIBLE_DEVICES and not all(dev.isdigit() for dev in CUDA_VISIBLE_DEVICES.split(",")):
            self.app_err(f"Config fault! CUDA_VISIBLE_DEVICES must be a comma-separated (',') list of integers. Current value: {CUDA_VISIBLE_DEVICES}")
            messagebox.showerror("Config fault!", "CUDA_VISIBLE_DEVICES must be a comma-separated (',') list of integers")
            error_code += 1024

        # bool check: 理论上这里不应该有错误，因为配置是程序自己弄的。但是为了防止用户自己手写json，还是检查一下。

        # Validate OLLAMA_ENABLE_CUDA
        if OLLAMA_ENABLE_CUDA not in ["0", "1", 0, 1]:
            self.app_err(f"Config fault! OLLAMA_ENABLE_CUDA must be 0 or 1. Current value: {OLLAMA_ENABLE_CUDA}")
            messagebox.showerror("Config fault!", "OLLAMA_ENABLE_CUDA must be 0 or 1")
            error_code += 2048

        # Validate OLLAMA_FLASH_ATTENTION
        if OLLAMA_FLASH_ATTENTION not in ["0", "1", 0, 1]:
            self.app_err(f"Config fault! OLLAMA_FLASH_ATTENTION must be 0 or 1. Current value: {OLLAMA_FLASH_ATTENTION}")
            messagebox.showerror("Config fault!", "OLLAMA_FLASH_ATTENTION must be 0 or 1")
            error_code += 4096

        # Validate OLLAMA_USE_MLOCK
        if OLLAMA_USE_MLOCK not in ["0", "1", 0, 1]:
            self.app_err(f"Config fault! OLLAMA_USE_MLOCK must be 0 or 1. Current value: {OLLAMA_USE_MLOCK}")
            messagebox.showerror("Config fault!", "OLLAMA_USE_MLOCK must be 0 or 1")
            error_code += 8192

        # Validate OLLAMA_MULTIUSER_CACHE
        if OLLAMA_MULTIUSER_CACHE not in ["0", "1", 0, 1]:
            self.app_err(f"Config fault! OLLAMA_MULTIUSER_CACHE must be 0 or 1. Current value: {OLLAMA_MULTIUSER_CACHE}")
            messagebox.showerror("Config fault!", "OLLAMA_MULTIUSER_CACHE must be 0 or 1")
            error_code += 16384

        # Validate OLLAMA_INTEL_GPU
        if OLLAMA_INTEL_GPU not in ["0", "1", 0, 1]:
            self.app_err(f"Config fault! OLLAMA_INTEL_GPU must be 0 or 1. Current value: {OLLAMA_INTEL_GPU}")
            messagebox.showerror("Config fault!", "OLLAMA_INTEL_GPU must be 0 or 1")
            error_code += 32768

        # Validate OLLAMA_DEBUG
        if OLLAMA_DEBUG not in ["0", "1", 0, 1]:
            self.app_err(f"Config fault! OLLAMA_DEBUG must be 0 or 1. Current value: {OLLAMA_DEBUG}")
            messagebox.showerror("Config fault!", "OLLAMA_DEBUG must be 0 or 1")
            error_code += 65536
        return error_code


if __name__ == "__main__":
    print('[info] run')
    try:      # high dpi 支持
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except ImportError:
        pass
    root = tk.Tk()
    app = OllamaLauncherGUI(root)
    root.mainloop()
    print('[info] ok')
