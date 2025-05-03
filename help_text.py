import tkinter as tk
from tkinter import ttk, scrolledtext
import webbrowser

VERSION = "v0.1a"
DATE = "2025年5月3日"

WELCONE_TEXT = f"\n\n\t\tOllama Launcher {VERSION} @ {DATE}\n\n\t\t\t\tWelcome!\n\n"

HELP_TEXT = '''
欢迎使用 Ollama Launcher！

这是一个用于管理和启动本地大语言模型（LLM）的图形化工具。

== 功能说明 ==

....

== 使用提示 ==

...

== 更多信息 ==

GitHub 项目主页: https://github.com/NGC13009/ollama-launcher.git
'''


def help_page():
    help_window = tk.Toplevel()
    help_window.title("Help - Ollama Launcher")
    help_window.geometry("800x600")
    help_window.minsize(800, 600)       # 设置最小大小
    help_window.iconbitmap('favicon.ico')
    bg_color = "#efefef"
    help_window.configure(bg=bg_color)
    text_area = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, width=80, height=20, bg=bg_color, fg="#1e1e1e", bd=0, highlightthickness=0)
    text_area.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)
    text_area.insert(tk.END, HELP_TEXT)
    text_area.config(state=tk.DISABLED) # 禁止用户编辑
    close_button = ttk.Button(help_window, text="X", command=help_window.destroy)
    close_button.pack(pady=5)
    help_window.update_idletasks()
    width = help_window.winfo_width()
    height = help_window.winfo_height()
    x = (help_window.winfo_screenwidth() // 2) - (width // 2)
    y = (help_window.winfo_screenheight() // 2) - (height // 2)
    help_window.geometry(f"{width}x{height}+{x}+{y}")


def about_page():
    about_window = tk.Toplevel()
    about_window.title("About Ollama Launcher ...")
    about_window.geometry("400x270")
    about_window.resizable(False, False)
    about_window.iconbitmap('favicon.ico')

    bg_color = "#efefef"
    fg_color = "#1e1e1e"
    about_window.configure(bg=bg_color)

    style = ttk.Style()
    style.configure("About.TFrame", background=bg_color)
    style.configure("About.TLabel", background=bg_color, foreground=fg_color)
    style.configure("About.TButton", background="#dcdad5", foreground=fg_color)

    # 容器 Frame
    container = ttk.Frame(about_window, style="About.TFrame")
    container.pack(expand=True, fill="both")

    info_text = f"""Ollama Launcher\n\nversion: {VERSION}\nupdate: {DATE}\nlicense: GPLv3\n- NGC13009 -"""

    label = tk.Label(container, text=info_text, justify="center", bg=bg_color, fg=fg_color)
    label.pack(pady=10)

    link = tk.Label(container, text="GitHub page: NGC13009/ollama-launcher.git", cursor="hand2", bg=bg_color, fg=fg_color)
    link.pack(pady=5)

    def callback(event):
        webbrowser.open_new(r"https://github.com/NGC13009/ollama-launcher.git")

    link.bind("<Button-1>", callback)

    close_button = ttk.Button(container, text="Close", style="About.TButton", command=about_window.destroy)
    close_button.pack(pady=10)
