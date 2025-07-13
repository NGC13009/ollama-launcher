# coding = utf-8
# Arch   = manyArch
#
# @File name:       utils.py
# @brief:           通用函数与类
# @attention:       None
# @Author:          NGC13009
# @History:         2025-07-13		Create

import ipaddress
import tkinter as tk
import re


def colorize_gin_log_Closure():
    """
    闭包。
    接收一个字符串（可能是 Gin 日志行），如果包含 "[GIN]"，
    则对 HTTP 状态码和方法及其周围空格应用 ANSI 背景色 (不包括 '|' 符号)。

    参数:
        log_line (str): 输入的日志字符串。

    返回:
        str: 带有 ANSI 颜色代码的字符串，或者如果输入不含 "[GIN]" 则返回原字符串。
    """

    BG_GREEN = "\x1b[42m"
    BG_YELLOW = "\x1b[43m"
    BG_RED = "\x1b[41m"
    BG_BLUE = "\x1b[44m"
    BG_CYAN = "\x1b[46m"
    BG_MAGENTA = "\x1b[45m"
    BG_WHITE = "\x1b[47m"
    BG_DEFAULT = "\x1b[49m"
    RESET = "\x1b[0m"

    def get_status_color(status_code_str):
        """根据 HTTP 状态码字符串返回合适的 ANSI 背景色代码。"""
        # (此函数保持不变)
        try:
            code = int(status_code_str)
            if 100 <= code < 200: return BG_BLUE
            elif 200 <= code < 300: return BG_GREEN
            elif 300 <= code < 400: return BG_CYAN
            elif 400 <= code < 500: return BG_YELLOW
            elif 500 <= code < 600: return BG_RED
            else: return BG_WHITE
        except ValueError:
            return BG_WHITE

    def get_method_color(method_str):
        """根据 HTTP 方法字符串返回合适的 ANSI 背景色代码。"""
        colors = {
            "GET": BG_BLUE,
            "POST": BG_GREEN,
            "PUT": BG_YELLOW,
            "DELETE": BG_RED,
            "PATCH": BG_MAGENTA,
            "HEAD": BG_CYAN,
            "OPTIONS": BG_WHITE,
        }
        return colors.get(method_str, BG_WHITE)

    def replace_method_modified(match):
        pipe_and_leading_spaces = match.group(1) # 例: "| "
        method = match.group(2)                  # 例: "GET"
        trailing_spaces = match.group(3)         # 例: "      "

        leading_spaces = pipe_and_leading_spaces[1:] # 提取第一个'|'后面的空格

        color = get_method_color(method)

        # 构造替换字符串: 第一个'|' + 颜色开始 + 前导空格 + 方法 + 尾随空格 + 颜色重置
        return f"|{color}{leading_spaces}{method}{trailing_spaces}{RESET}"

    def replace_status_modified(match):
        pipe_and_leading_spaces = match.group(1)  # 例: "|  "
        status_code = match.group(2)              # 例: "200"
        trailing_spaces_and_pipe = match.group(3) # 例: "  |"

        leading_spaces = pipe_and_leading_spaces[1:]    # 提取第一个'|'后面的空格
        trailing_spaces = trailing_spaces_and_pipe[:-1] # 提取最后一个'|'前面的空格

        color = get_status_color(status_code)

        # 构造替换字符串: 第一个'|' + 颜色开始 + 前导空格 + 状态码 + 尾随空格 + 颜色重置 + 第二个'|'
        return f"|{color}{leading_spaces}{status_code}{trailing_spaces}{RESET}|"

    status_pattern_original = r'(\|\s*)(\d{3})(\s*\|)'
    method_pattern_original = r'(\|\s*)(\b(?:GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\b)(\s+)'

    def color_line(log_line):
        if "[GIN]" not in log_line:
            return log_line

        log_line = re.sub(status_pattern_original, replace_status_modified, log_line)
        log_line = re.sub(method_pattern_original, replace_method_modified, log_line)
        return log_line

    return color_line


colorize_gin_log = colorize_gin_log_Closure()


def validate_spinbox(value_if_allowed):
    """数字输入框不能出现乱七八糟的东西"""
    if value_if_allowed == "":
        return True
    return bool(re.fullmatch(r"^-?\d*$", value_if_allowed))


def is_valid_host_port(host_string: str) -> bool:
    """
    校验一个字符串是否是合法的 'ip:port' 或 'hostname:port' 格式。
    
    Args:
        host_string: 需要校验的字符串。

    Returns:
        如果格式合法则返回 True，否则返回 False。
    """
    if not isinstance(host_string, str):
        return False
    last_colon_pos = host_string.rfind(':')
    if last_colon_pos == -1:
        return False

    host_part = host_string[:last_colon_pos]
    port_part = host_string[last_colon_pos + 1:]

    if not port_part.isdigit():
        return False
    try:
        port = int(port_part)
        if not (0 <= port <= 65535):
            return False
    except ValueError:
        return False

    if host_part.startswith('[') and host_part.endswith(']'):
        host_part = host_part[1:-1]

    if host_part.lower() == 'localhost':
        return True

    try:
        ipaddress.ip_address(host_part)
        return True
    except ValueError:
        return False


# 彩色打印以支持ANSI着色
class AnsiColorText(tk.Text):

    def __init__(self, master=None, **kwargs):
        default_bg = '#1e1e1e'
        default_fg = '#efefef'

        kwargs.setdefault('background', default_bg)
        kwargs.setdefault('foreground', default_fg)
        kwargs.setdefault('insertbackground', 'white')
        kwargs.setdefault('state', tk.NORMAL) # 修改为 NORMAL

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
            '30': {'foreground': '#1e1e1e'},  # Black (use dark gray)
            '31': {'foreground': '#cd3131'},  # Red
            '32': {'foreground': '#0dbc79'},  # Green
            '33': {'foreground': '#e5e510'},  # Yellow
            '34': {'foreground': '#4e8fd4'},  # Blue
            '35': {'foreground': '#bc3fbc'},  # Magenta
            '36': {'foreground': '#11a8cd'},  # Cyan
            '37': {'foreground': '#e5e5e5'},  # White (use light gray)
            '39': {'foreground': default_fg}, # Default foreground

            # --- 添加亮色前景 (90-97) ---
            '90': {'foreground': '#1e1e1e'},  # Bright Black (darker gray)
            '91': {'foreground': '#cd3131'},  # Bright Red
            '92': {'foreground': '#0dbc79'},  # Bright Green
            '93': {'foreground': '#e5e510'},  # Bright Yellow
            '94': {'foreground': "#4e8fd4"},  # Bright Blue
            '95': {'foreground': '#bc3fbc'},  # Bright Magenta
            '96': {'foreground': '#11a8cd'},  # Bright Cyan
            '97': {'foreground': '#e5e5e5'},  # Bright White

            # Background colors (40-47)
            '40': {'background': '#1e1e1e'},  # Black background
            '41': {'background': '#cd3131'},  # Red background
            '42': {'background': '#0dbc79'},  # Green background
            '43': {'background': '#e5e510'},  # Yellow background
            '44': {'background': '#4e8fd4'},  # Blue background
            '45': {'background': '#bc3fbc'},  # Magenta background
            '46': {'background': '#11a8cd'},  # Cyan background
            '47': {'background': '#e5e5e5'},  # White background
            '49': {'background': default_bg},  # Default background
            'sel' : {'background': '#264f78', 'foreground': '#efefef'},  # 选中时的样式
        }
        # yapf: enable

        # --- Configure tags ---
        for code, config in self.tag_configs.items():
            tag_name = f"ansi_{code}"
            self.tag_configure(tag_name, **config)

        # Keep track of currently active SGR codes for applying tags
        self.active_codes = {'0'} # Start with reset state

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
        self.config(state=tk.NORMAL) # Enable writing

        # 判断插入前是否贴底
        was_at_bottom = (self.yview()[1] == 1.0)

        # Split text by ANSI codes, keeping the codes as delimiters
        parts = self.ansi_escape_pattern.split(text)

        for i, part in enumerate(parts):
            if not part: # Skip empty parts
                continue

            if i % 2 == 0:
                # This is plain text
                # Determine tags based on active codes, excluding '0' unless it's the only one
                current_tags = tuple(f"ansi_{code}" for code in self.active_codes if code != '0')
                self.insert(tk.END, part, current_tags + ("sel", )) # 添加 sel 标签
            else:
                                                                    # This is ANSI code
                codes = part.split(';')
                needs_reset = False
                new_codes_in_sequence = set()

                for code in codes:
                    if not code:
                        continue
                    code = code.lstrip('0')
                    if not code:
                        code = '0'

                    if code == '0':
                        needs_reset = True
                        break
                    if code in self.tag_configs:
                        new_codes_in_sequence.add(code)

                if needs_reset:
                    self.active_codes = {'0'}
                else:
                    temp_active = set(self.active_codes)
                    for new_code in new_codes_in_sequence:
                        if '30' <= new_code <= '37' or new_code == '39':
                            temp_active = {c for c in temp_active if not ('30' <= c <= '37' or c == '39')}
                        elif '40' <= new_code <= '47' or new_code == '49':
                            temp_active = {c for c in temp_active if not ('40' <= c <= '47' or c == '49')}
                        elif new_code == '22':
                            temp_active.discard('1')
                        elif new_code == '24':
                            temp_active.discard('4')
                    temp_active.update(new_codes_in_sequence)
                    if len(temp_active) > 1:
                        temp_active.discard('0')
                    elif not temp_active:
                        temp_active = {'0'}
                    self.active_codes = temp_active

        # 插入完成后，根据贴底状态决定是否滚动到底部
        if was_at_bottom:
            self.see(tk.END)

    def copy_selection(self, event):
        """复制选中的文本到剪贴板."""
        try:
            selected_text = self.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected_text)
            return "break" # 阻止默认行为
        except tk.TclError:
                           # 没有选中内容
            return "break"
