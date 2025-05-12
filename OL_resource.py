# coding = utf-8
# Arch   = manyArch
#
# @File name:       ollama_launcher.py
# @brief:           ollama launcher 启动器资源包：这里内容比较占地方, 拿出来
# @attention:       None
# @TODO:            None
# @Author:          NGC13009
# @History:         2025-05-03		Create

# 草泥马图标
icon_base64_data = '''AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACQkJDCAAAA/w8PD/b6+vrQ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////+vr60A8PD/YAAAD/kJCQwisrK8IAAAD/GBgY////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////GBgY/wAAAP8rKyvCAAAAxgAAAP8YGBj///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////8YGBj/AAAA/wAAAMYAAAC2AAAA/xgYGP/////////////////////////////////////////////////9/f3039/f7MzMzP/MzMz/zMzM/8zMzP/f39/s/f399P///////////////////////////////////////////////xgYGP8AAAD/AAAAtlpaWrgAAAD/GBgY////////////////////////////////////////////5eXlwlJSUuwFBQXcAAAA/wAAAP8AAAD/AAAA/wUFBdxSUlLs5eXlwv//////////////////////////////////////////GBgY/wAAAP9aWlq4x8fH/wAAAP8CAgL2sLCw1P///////////////////////////v7+/7KyssgAAAD/AgIC/wcHB/9DQ0O8jIyM7oyMjO5DQ0O8BwcH/wICAv8AAAD/srKyyP7+/v///////////////////////////7CwsNQCAgL2AAAA/8fHx//S0tLyAAAA6gAAAP9mZmbS/////P/////////////////////q6ur0HR0d5gQEBPyrq6vo/v7++v/////////////////////+/v76q6ur6AQEBPwdHR3m6urq9P/////////////////////////8ZmZm0gAAAP8AAADq0tLS8vv7+/pNTU34AAAA/wMDA/D4+Pj//////////////////////9fX1/8AAAD/xsbGzP///////////////1VVVf9VVVX/////////////////xsbGzAAAAP/X19f///////////////////////j4+P8DAwPwAAAA/01NTfj7+/v6+fn5+klJSfYAAAD/AAAA//f39///////////////////////iYmJmAAAAP/////////////////p6en8KSkp/ykpKfzs7Oz6////////////////AAAA/4mJiZj/////////////////////9/f3/wAAAP8AAAD/TU1N6vz8/PbS0tL4CAgI9gAAAP9dXV3//Pz8///////////////////////Hx8feAAAA/+Dg4LL//////////6ioqPwAAAD/AAAA+qurq/j//////////+Dg4LIAAAD/x8fH3v/////////////////////8/Pz/XV1d/wAAAP8ICAjw1dXV9n5+fsIAAAD/BwcH9NjY2Mj//////////+vr6/8YGBiqoqKi2tra2voHBwf6BwcH//Pz8//////////////////////////////////z8/P/BwcH/wcHB/ra2tr6oqKi2hgYGKrr6+v///////////+zs7PgBAQE+AAAAP+srKzSAAAA4gAAAP8ZGRn0////////////////KSkp+gAAAP8AAAD/nJycwoCAgNgAAAD/PDw8/Kenp9L/////////////////////p6en0jw8PPwAAAD/gICA2JycnMIAAAD/AAAA/ykpKfr///////////////8YGBj/AAAA/x8fH9YAAAD/AAAA/x4eHsj///////////////8pKSn2AAAA/wAAAP87Ozuu+/v7+nJycpQAAAD/AgIC+BMTE/8TExP/ExMT/xMTE/8CAgL4AAAA/3JycpT7+/v6Ozs7rgAAAP8AAAD/KSkp9v///////////////xsbG+QAAAD/AAAA/AAAAP8AAAD/SkpK4P////////////////////9XV1f/V1dX/////////////////8bGxuJZWVn4MTEx3iwsLPosLCz6MTEx3llZWfjGxsbi////////////////V1dX/1dXV///////////////////////HBwc3gAAAP8AAAD/AAAA/AAAAP8aGhrs///////////////////////////////////////////////////////////39/fm4+Pj/OPj4/z39/fm//////////////////////////////////////////////////////////8YGBj6AAAA/wAAANwbGxusAAAA/xQUFPz19fX2////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////8PDw+hQUFP8AAAD/Z2dnwLm5udwAAAD/AQEB+pqamur///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////+Ojo7yAAAA/AAAAP/Hx8f/7e3t6B4eHtoAAAD/AQEB9Pj4+P//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////9/f3/wEBAfoAAAD/Hh4e2u3t7ej/////mpqa8AAAAP8AAAD/AAAA4ru7u+r////2/////////////////////////////////////////////////////////////////////////////////////////////////v7++Lq6uuwAAAD2AAAA/wAAAP+amprw///////////////6s7Oz6AAAAP8AAAD/CQkJ9ioqKvikpKTU29vbrr29vdb+/v7s//////////////////////////////////////////////////////v7+/C9vb3W3Nzcrnd3d54pKSn8CQkJ9gAAAP8AAAD/s7Oz6P////r////////////////////8cnJy9gAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/4aGhuz/////////////////////////////////////////////////////goKC9AAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/3Jycvb////8//////////////////////////94eHj/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/Dw8P4v39/dL///////////////////////////////////////////Dw8N4ODg7uAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/eHh4/////////////////////////////////3h4eP8AAAD/AAAA1uXl5e7//////////wAAAP8AAAD/BQUF/93d3eL9/f3///////////////////////39/fi+vr60AQEB+gAAAP8AAAD////////////l5eXuAAAA1gAAAP94eHj/////////////////////////////////eHh4/wAAAP8AAAC68PDw5P//////////AAAA/wAAAP8AAAD/AAAA8np6evyNjY3ux8fH5sXFxeiMjIzwWlpa0AAAAPgAAAD/AAAA/wAAAP////////////Dw8OQAAAC6AAAA/3h4eP////////////////////////////////94eHj/AAAA/wAAAMLs7Ozo//////////8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAPoKCgr6CgoK+gAAAPwAAAD/AAAA/wAAAP8AAAD/AAAA////////////7Ozs6AAAAMIAAAD/eHh4/////////////////////////////////3h4eP8AAAD/AAAA7N3d3fj//////////wAAAP8AAAD/f39/jlNTU/IkJCTyAAAA/AAAAP8AAAD/AAAA+iQkJO5WVlbqgYGBjAAAAP8AAAD////////////d3d34AAAA7AAAAP94eHj/////////////////////////////////fHx89gAAAP8AAAD/19fX//////+4uLjiAAAA/wAAAP/6+vra/////+Li4vS5ubn8uLi4/7i4uP+7u7v65ubm8P/////6+vraAAAA/wAAAP+4uLji/////9fX1/8AAAD/AAAA/3x8fPb////////////////////////////////V1dWkAQEB+gAAAP+4uLji/////0pKSvgAAAD/AAAA9v////////////////////////////////////////////////////8AAAD2AAAA/0pKSvj/////uLi44gAAAP8BAQH61dXVpP////////////////////////////////////oICAj/AAAA/wAAANzW1tb2ICAg/AAAAP9MTEzQ/////////////////////////////////////////////////////0xMTNAAAAD/ICAg/NbW1vYAAADcAAAA/wgICP/////6/////////////////////////////////////83NzZIAAAD/AAAA/wUFBf8AAAD/AAAA+KCgoO7/////////////////////////////////////////////////////oKCg7gAAAPgAAAD/BQUF/wAAAP8AAAD/zc3Nkv///////////////////////////////////////////////z09PfAAAAD8AAAA/wAAAP9wcHDw////////////////////////////////////////////////////////////////cHBw8AAAAP8AAAD/AAAA/D09PfD/////////////////////////////////////////////////////7Ozs/LW1tbKFhYXCwMDA5v39/fj////////////////////////////////////////////////////////////////9/f34wMDA5oWFhcK1tbWy7Ozs/P//////////////////////////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA='''

VERSION = "v2.0"
DATE = "2025Y5M13D"

# 欢迎标语 : 彩色的
WELCONE_TEXT = f"\n\n\t\t    Ollama Launcher {VERSION} @ {DATE}\n\n\t\t\t\tWelcome!\n\n\t\t\t\x1b[40m  \x1b[0m \x1b[47m  \x1b[0m \x1b[44m  \x1b[0m \x1b[43m  \x1b[0m \x1b[41m  \x1b[0m \x1b[46m  \x1b[0m \x1b[42m  \x1b[0m \x1b[45m  \x1b[0m \x1b[49m  \x1b[0m\n\n\tHow to use: See Help & About information in the 'Info'\n\ttab of the menu bar.\n\n"

# 关于页的提示文本
INFO_TEXT = f"""Ollama Launcher\n\nversion: {VERSION}\nupdate: {DATE}\nlicense: GPLv3\n- NGC13009 -"""
GITLINK = r"https://github.com/NGC13009/ollama-launcher.git"
GITLINK_BOTTOM = "NGC13009/ollama-launcher.git"

# 帮助页的提示文本
HELP_TEXT = '''
欢迎使用 Ollama Launcher!
Welcome to use Ollama Launcher!

# English Help Document is available at the end of Chinese Help Document.

更好的帮助文档请查看本项目的GitHub页面。
# Better help document can be found on the GitHub page of this project.

-- https://github.com/NGC13009/ollama-launcher.git --

你也可以通过启动器的菜单栏-Info-About内的按钮, 来快速访问上面的链接。
You can also quickly access the link through the button located in the launcher's menu bar under **Info > About**.

----------------------------------------

# ollama-launcher
更好的ollama服务启动器

欢迎使用 Ollama Launcher！

### 快速开始

ollama-launcher的直接可执行文件下载链接 : [click here](https://github.com/NGC13009/ollama-launcher/releases/)

从[这里](https://github.com/ollama/ollama/releases/)下载zip版本的ollama, 解压到一个路径, 然后配置 ollama launcher 中 ollama 的路径, 即可使用启动器来管理启动 `ollama serve` 守护进程。避免自动升级, 轻松配置启动参数, 同时方便查看彩色的日志。

你也可以通过启动器上方的菜单栏, 获取最新版的 ollama zip 的下载链接。

### 简介

- Ollama Launcher 是 ollama 的启动器, 可以方便地启动和管理 ollama 服务进程。
- Ollama Launcher 旨在简化配置ollama server的启动参数。免去不断修改环境变量与启动停止守护进程的麻烦。如此一来, 修改ollama守护进程的运行参数, 启停服务进程将会更加方便。
- Ollama Launcher 不能管理模型, 即只能启动和停止 ollama 服务进程, 不能拉取, 运行, 配置模型。为了配置模型, 你仍旧需要使用命令行。

启动器主要是为了避免自动更新, 以及更方便的设置启动参数。为此, 推荐使用二进制可执行文件替代ollama setup的安装方式: [ollama download](https://github.com/ollama/ollama/releases) , 下载zip压缩包并解压到某个路径下, 将`ollama.exe`配置为系统环境变量`Path`内, 之后启动 ollama-launcher 并配置`ollama.exe`的路径即可。

如果仍旧希望自动更新, 则从ollama官网: [ollama](https://ollama.com/) 下载setup安装程序直接安装, 然后找到`ollama.exe`的路径配置即可。注意需要关闭ollama的默认开机自启动, 以使用ollama-launcher完全代理后台服务。需要更新时, 关闭ollama-launcher, 使用安装的ollama启动, 即可自动更新。

如果您使用ollama setup安装, 那么默认路径是：
`C:\\Users\\<你的用户名>\\AppData\\Local\\Programs\\Ollama\\ollama.exe`
, 你需要将这个地址配置为ollama-launcher内启动ollama的地址。
此外, 你还可以直接自定义模型的存储路径(默认是在C盘) 。注意, 这个操作不会自动搬移已经下载的模型。

## 说明书须知

+ 下面的功能说明也是AI生成的, 作者并未严格审核内容, 只是大概看了一眼。
+ 由于工作量原因, 暂时没有中文版。(不过这几个单词也没啥难看懂的吧, 何况这里有一个说明) 
+ 中文说明是准确的, 英文说明是机翻的, 没有严格审查内容, 不承诺准确性。
+ 说明书仅供参考

## 功能说明

Ollama Launcher 的功能包括以下几点：
1. 启动 ollama 服务进程(`ollama serve`) 
2. 停止 ollama 服务进程(`ollama serve`) 
3. 配置启动参数(ollama通过环境变量设置启动参数, 如端口、运行上下文, 运行的CUDA加速设备) 
4. 支持最小化到托盘
5. 支持启动后直接进入后台托盘
6. 方便的查看ollama服务运行日志
7. 避免ollama升级提示(坏处是需要手动更新了) 
8. 跨平台(除了Windows, 其他平台没测试过, 需要自行使用pyinstaller编译) 

## 使用提示

Ollama 启动器旨在简化 Ollama 服务进程的管理。界面主要分为左右两个区域, 以及顶部的菜单栏、底部的状态栏和操作按钮。

### 1. 左侧区域 (配置区)

#### 1.1. 环境变量与选项

最上方的：**Ollama Executable Path**: 用于指定 `ollama.exe`(或对应操作系统的可执行文件) 所在的完整路径。用户可以通过输入框手动输入, 或点击右侧的 "..." 按钮浏览文件系统来选择。
最下方的：**复选框 (Auto start ollama & hide to tray on launch)**: 勾选后, 当启动这个 Ollama Launcher 程序时, 它会自动尝试启动 Ollama 服务, 并将自身窗口最小化到系统托盘区。

#### 1.2. Environment Variables & Options

这是核心配置区域, 以列表形式展示了可以传递给 Ollama 服务器的各种环境变量和启动选项。用户可以直接在对应的文本框中修改这些值。

1.    **OLLAMA_MODELS**: 控制 模型存储位置。指定 Ollama 从哪里加载以及将下载的模型文件保存到哪个磁盘目录。
2.    **OLLAMA_TMPDIR**: 控制 临时文件位置。指定 Ollama 在运行过程中(如模型解压、转换时) 存放临时文件的目录。
3.    **OLLAMA_HOST**: 控制 网络监听配置。决定 Ollama 服务绑定到哪个网络接口(IP 地址) 以及使用哪个端口号来接收客户端的请求。这影响了服务的可访问性(本机访问还是局域网访问) 。
4.    **OLLAMA_ORIGINS**: 控制 API 访问权限 (CORS)。设置允许哪些来源(域名、IP地址) 的前端应用跨域调用 Ollama 的 API 接口。这是浏览器的安全策略控制。
5.    **OLLAMA_CONTEXT_LENGTH**: 控制 模型处理能力 (上下文窗口)。设定模型能够理解和生成的最大文本长度(上下文窗口大小) , 以 token 数量衡量。
6.    **OLLAMA_KV_CACHE_TYPE**: 控制 模型缓存精度。配置模型在推理时使用的 Key/Value 缓存的量化类型, 影响内存占用和可能的性能/精度平衡。
7.    **OLLAMA_KEEP_ALIVE**: 控制 模型加载时长。指定一个模型在没有被使用后, 在内存(RAM 或 VRAM) 中保持加载状态多长时间。影响再次调用该模型时的响应速度和系统资源占用。
8.    **OLLAMA_MAX_QUEUE**: 控制 请求排队上限。当服务器繁忙时, 能接收并放入等待队列处理的最大请求数量。影响高并发下的请求处理能力。
9.    **OLLAMA_NUM_PARALLEL**: 控制 并行处理能力。设置 Ollama 可以同时处理多少个推理请求。影响服务器的吞吐量和资源利用率。
10.   **OLLAMA_ENABLE_CUDA**: 控制 NVIDIA GPU 加速。决定是否启用 NVIDIA 的 CUDA 技术来利用 GPU 进行计算加速。
11.   **CUDA_VISIBLE_DEVICES**: 控制 使用的 NVIDIA GPU。如果系统有多块 NVIDIA GPU, 这个变量指定 Ollama 应该使用哪一块或哪几块 GPU(通过索引号) 。
12.   **OLLAMA_FLASH_ATTENTION**: 控制 特定优化技术。决定是否启用 FlashAttention 算法(一种优化 Transformer 注意力计算的方法) , 可以在兼容的硬件上提升推理速度并减少显存占用。
13.   **OLLAMA_USE_MLOCK**: 控制 内存锁定行为 (主要用于 Linux/macOS)。决定是否尝试将模型数据锁定在物理内存(RAM) 中, 防止操作系统将其交换到速度较慢的硬盘上, 以保证性能稳定性。
14.   **OLLAMA_MULTITASK_CACHE**: 控制 多任务缓存策略。调整与同时运行多个模型或处理多类型任务相关的缓存机制, 可能影响这些场景下的性能。
15.   **OLLAMA_INTEL_GPU**: 控制 Intel GPU 加速。决定是否尝试启用 Intel 的集成显卡或独立显卡进行计算加速。
16.   **OLLAMA_DEBUG**: 控制 日志详细程度。决定 Ollama 是否输出更详细的调试信息到日志中, 用于问题排查。

这些项目是用来配置 Ollama 服务器行为的环境变量。修改这些值会影响 Ollama 服务启动后的运行方式：

#### 1.3. 操作按钮

- **Ollama Run**: 启动 Ollama 服务进程。
- **Ollama Stop**: 停止当前正在运行的 Ollama 服务进程。
- **Copy Log**: 复制右侧日志区域的全部内容到剪贴板。
- **Clear Log**: 清空右侧日志区域显示的内容。
- **Hide to tray**: 将当前启动器窗口最小化到系统托盘区。
- **底部状态栏**：显示最近一次的操作状态。

### 2. 右侧区域 (日志输出区)

**Ollama Log Output**: 这是一个文本显示区域, 用于实时展示 Ollama 服务进程的启动信息、运行状态、警告、错误以及该启动器本身的操作日志。可以看到时间戳、日志级别([app info], [app warn] 等) 和具体的日志内容。

### 3. 顶部菜单栏

包含 **App**, **Action**, **Info** 三个菜单项。

#### 3.1. App 菜单

- **Hide to Tray**: 将 Ollama Launcher 程序的窗口最小化到系统托盘区(任务栏通知区域) 。这和主界面上的 "Hide to tray" 按钮功能相同。
- **Print Welcome**: 在右侧的日志输出区域重新打印程序启动时的欢迎信息。
- **Edit additional Environment**: 编辑额外的环境变量。允许用户添加或修改一些没有在主界面“Environment Variables & Options”列表中默认显示的其他 Ollama 环境变量, 或者是以不同方式管理它们。
- **Save Config**: 保存当前的配置。将你在界面上做的所有更改(包括 Ollama 可执行文件路径、所有环境变量的值等) 保存到配置文件中(就是状态栏提到的 `config.json`) , 以便下次启动时加载这些设置。其实不用手动保存, 因为程序退出时是自动- 保存的。
- **Reset Config**: 重置配置。将所有设置恢复到程序的默认状态或初始配置文件状态。
- **Exit**: 退出 Ollama Launcher 应用程序。

#### 3.2. Action 菜单

- **▶ Ollama Run**: 启动 Ollama 服务进程。这和主界面上的 "Ollama Run" 按钮功能相同, 前面的 "▶" 图标表示启动/运行。
- **■ Ollama Stop**: 停止当前正在运行的 Ollama 服务进程。这和主界面上的 "Ollama Stop" 按钮功能相同, 前面的 "■" 图标表示停止。
- **Save Log**: 保存日志。将右侧“Ollama Log Output”区域显示的日志内容保存到一个文本文件中。
- **Copy Log**: 复制日志。将右侧日志区域的全部内容复制到系统剪贴板。这和主界面上的 "Copy Log" 按钮功能相同。
- **Clear Log**: 清除日志。清空右侧日志区域显示的内容。这和主界面上的 "Clear Log" 按钮功能相同。

#### 3.3. Info 菜单

- **Help**: 显示此页面的帮助信息。
- **About**: 显示关于信息。会弹出一个窗口, 显示这个 Ollama Launcher 程序的名称、版本号、开发者信息、版权声明等。

### 4. 系统托盘

右键系统托盘可获取一个菜单, 这在最小化到托盘时操作将很方便。

- **Show Launcher**: 显示启动器。点击这个选项会将之前隐藏或最小化到托盘的 Ollama Launcher 主窗口重新显示出来, 放到屏幕最前面。
- **▶ Ollama Run**: 运行 Ollama。用于启动 Ollama 服务进程。这和主窗口中的 "Ollama Run" 按钮以及 "Action" 菜单里的 "Ollama Run" 功能相同。
- **■ Ollama Stop**: 停止 Ollama。用于停止当前正在运行的 Ollama 服务进程。这和主窗口中的 "Ollama Stop" 按钮以及 "Action" 菜单里的 "Ollama Stop" 功能相同。
- **Exit**: 退出。完全关闭 Ollama Launcher 这个应用程序。通常情况下, 退出启动器也会停止由它启动的 Ollama 服务进程。

### 5. 通知

启动器在ollama服务启动和停止的时候会通过系统通知渠道发送提示。

1. **启动提示**：`ollama serve` 启动时, 展示启动的ollama服务 PID 进程号信息, 以及当前时间戳。
2. **停止提示**：`ollama serve` 由于一些原因(用户操作或者异常退出) 导致停止时, 显示ollama服务的停止退出代码以及当前时间戳。

### 6. 弹出窗口

一些错误会导致不可忽略的中断, 这些信息被设计为通过弹出窗口提示, 以更加醒目的消息提醒用户。

## 获取更多帮助 / 问题反馈 / 新添加功能讨论

[GitHub 项目主页](https://github.com/NGC13009/ollama-launcher.git )

请联系作者或提交issue。你可以通过About页面下方的按钮在浏览器打开此页面。

----------------


----------------

# ollama-launcher
A Better Ollama Service Launcher

Welcome to Ollama Launcher!

### Quick Start

Download the standalone executable for ollama-launcher: [click here](https://github.com/NGC13009/ollama-launcher/releases/)

Download the zip version of Ollama from [here](https://github.com/ollama/ollama/releases/) , extract it to a directory, and then configure the Ollama path in Ollama Launcher. You can then use the launcher to manage the startup of the `ollama serve` daemon. Avoid automatic updates, easily configure startup parameters, and conveniently view colored logs.

You can also obtain the latest Ollama zip download link via the menu bar at the top of the launcher.

### Introduction

- Ollama Launcher is a launcher for Ollama, which allows you to easily start and manage the Ollama service process.
- Ollama Launcher aims to simplify the configuration of startup parameters for the Ollama server. It eliminates the need to constantly modify environment variables or manually start/stop the background service. As a result, changing runtime parameters for the Ollama background service and managing service processes becomes much more convenient.
- Ollama Launcher does not manage models. That means it can only start and stop the Ollama service process, but cannot pull, run, or configure models. To manage models, you still need to use the command line.

The launcher is primarily designed to avoid automatic updates and provide easier configuration of startup parameters. Therefore, it is recommended to use the binary executable instead of installing via Ollama's setup installer: [Ollama download](https://github.com/ollama/ollama/releases ), download the zip package, extract it to a directory, add the `ollama.exe` path to your system's `Path` environment variable, then launch Ollama-Launcher and configure the path to `ollama.exe`.

If you prefer automatic updates, you can download the setup installer from the official Ollama website: [Ollama](https://ollama.com/ ) and install it directly. Then locate the `ollama.exe` path and configure it in Ollama Launcher. Please note that you should disable the default auto-start of Ollama at boot so that Ollama Launcher can fully manage the background service. When updating is needed, close Ollama Launcher first and start Ollama using the installed version to trigger an automatic update.

If you installed Ollama via the setup installer, the default installation path is:
`C:\\Users\\<YourUsername>\\AppData\\Local\\Programs\\Ollama\\ollama.exe`
You need to set this path as the executable path within Ollama Launcher.

Additionally, you can customize the storage path for models (by default stored on the C drive). Note that this operation will not automatically move already downloaded models.

## Notes for the User Manual

+ The following functional descriptions are generated by AI. The author has not strictly reviewed the content, only briefly checked it.
+ Due to workload considerations, a Chinese version is temporarily unavailable. (But there's not much difficult vocabulary here that should be hard to understand, after all, there is an explanation)
+ The Chinese instructions are accurate, while the English ones are machine-translated. The content has not been rigorously reviewed, and accuracy is not guaranteed.
+ The manual is for reference only

## Feature Description

Ollama Launcher includes the following features:
1. Start the Ollama service process (`ollama serve`)
2. Stop the Ollama service process (`ollama serve`)
3. Configure startup parameters (Ollama uses environment variables to set startup options, such as port, context size, and CUDA acceleration devices)
4. Support for minimizing to the system tray
5. Option to directly run in the background system tray upon startup
6. Convenient viewing of Ollama service runtime logs
7. Avoid Ollama update notifications (the downside is that you will need to update manually)
8. Cross-platform support (although only Windows has been tested; other platforms require self-compilation using PyInstaller)

## Usage Instructions

The Ollama Launcher is designed to simplify the management of the Ollama service process. The interface is mainly divided into two areas — left and right — along with a top menu bar, a bottom status bar, and action buttons.

### 1. Left Area (Configuration Panel)

#### 1.1 Environment Variables and Options

At the top: **Ollama Executable Path** — This field is used to specify the full path to the `ollama.exe` file (or the corresponding executable for your operating system). Users can either manually enter the path in the input box or click the "..." button on the right to browse the file system and select it.

At the bottom: **Checkbox (Auto start ollama & hide to tray on launch)** — When checked, launching the Ollama Launcher will automatically attempt to start the Ollama service and minimize the launcher window directly to the system tray.

#### 1.2 Environment Variables & Options

This is the core configuration area, which presents a list of various environment variables and startup options that can be passed to the Ollama server. Users can directly modify these values in the corresponding text fields.

1. **OLLAMA_MODELS**: Controls the **model storage location**. Specifies where Ollama loads models from and where downloaded model files are saved on disk.
2. **OLLAMA_TMPDIR**: Controls the **temporary file location**. Sets the directory where Ollama stores temporary files during operation (e.g., during model extraction or conversion).
3. **OLLAMA_HOST**: Controls **network interface binding**. Determines which network interface (IP address) and port number the Ollama service listens on for client requests. This affects whether the service is accessible locally or over the network.
4. **OLLAMA_ORIGINS**: Controls **API access permissions (CORS)**. Sets which origins (domains, IP addresses) are allowed to make cross-origin API calls to Ollama. This is related to browser security policies.
5. **OLLAMA_CONTEXT_LENGTH**: Controls **model processing capacity (context window)**. Sets the maximum length of text (in tokens) that the model can understand and generate — i.e., the size of the context window.
6. **OLLAMA_KV_CACHE_TYPE**: Controls **model cache precision**. Configures the quantization type used for Key/Value caches during inference, affecting memory usage and potentially performance or accuracy.
7. **OLLAMA_KEEP_ALIVE**: Controls **model loading duration**. Specifies how long a model remains loaded in memory (RAM or VRAM) after it has not been used. Affects response speed when the model is called again and system resource usage.
8. **OLLAMA_MAX_QUEUE**: Controls **maximum request queue size**. When the server is busy, this sets the maximum number of incoming requests that can be queued for processing. Impacts handling capacity under high concurrency.
9. **OLLAMA_NUM_PARALLEL**: Controls **parallel processing capability**. Sets how many inference requests Ollama can process simultaneously. Affects server throughput and resource utilization.
10. **OLLAMA_ENABLE_CUDA**: Controls **NVIDIA GPU acceleration**. Determines whether NVIDIA CUDA technology is used to leverage GPU computing power for acceleration.
11. **CUDA_VISIBLE_DEVICES**: Controls **which NVIDIA GPUs to use**. If multiple NVIDIA GPUs are present in the system, this variable specifies which one(s) Ollama should use (by index number).
12. **OLLAMA_FLASH_ATTENTION**: Controls a **specific optimization technique**. Determines whether to enable the FlashAttention algorithm (an optimized method for Transformer attention computation), which can improve inference speed and reduce GPU memory usage on compatible hardware.
13. **OLLAMA_USE_MLOCK**: Controls **memory locking behavior (mainly for Linux/macOS)**. Determines whether to attempt to lock model data in physical memory (RAM) to prevent the operating system from swapping it to slower disk storage, ensuring performance stability.
14. **OLLAMA_MULTITASK_CACHE**: Controls **multi-task caching strategy**. Adjusts caching mechanisms related to running multiple models or handling different types of tasks simultaneously, which may impact performance in those scenarios.
15. **OLLAMA_INTEL_GPU**: Controls **Intel GPU acceleration**. Determines whether to try using Intel integrated or discrete GPUs for computational acceleration.
16. **OLLAMA_DEBUG**: Controls **log verbosity**. Determines whether Ollama outputs more detailed debugging information to logs, useful for troubleshooting issues.

These items are environment variables used to configure the behavior of the Ollama server. Modifying these values will affect how the Ollama service operates after it is started:

#### 1.3 Action Buttons

- **Ollama Run**: Starts the Ollama service process.
- **Ollama Stop**: Stops the currently running Ollama service process.
- **Copy Log**: Copies all content from the log area on the right to the clipboard.
- **Clear Log**: Clears the displayed content in the log area on the right.
- **Hide to Tray**: Minimizes the launcher window to the system tray.
- **Bottom Status Bar**: Displays the status of the most recent operation.

### 2. Right Area (Log Output Panel)

**Ollama Log Output**: This is a text display area that shows, in real-time, the startup messages, runtime status, warnings, and errors from the Ollama service process, as well as operation logs from the launcher itself. The logs include timestamps, log levels (e.g., [app info], [app warn]), and the

### 3. Top Menu Bar

Contains three menu items: **App**, **Action**, and **Info**.

#### 3.1 App Menu

- **Hide to Tray**: Minimizes the Ollama Launcher window to the system tray (notification area of the taskbar). This function is the same as the "Hide to tray" button on the main interface.
- **Print Welcome**: Reprints the welcome message that appears at program startup into the log output area on the right.
- **Edit additional Environment**: Edit additional environment variables. Allows users to add or modify other Ollama-related environment variables that are not displayed by default in the "Environment Variables & Options" list on the main interface, or manage them in different ways.
- **Save Config**: Saves the current configuration. All changes made in the interface (including the Ollama executable path, values of all environment variables, etc.) will be saved to a configuration file (the `config.json` mentioned in the status bar), so they can be loaded the next time the program starts. Manual saving is usually unnecessary, as the application automatically saves settings when exiting.
- **Reset Config**: Resets the configuration. Restores all settings to their default values or the initial state defined in the configuration file.
- **Exit**: Exits the Ollama Launcher application.

#### 3.2 Action Menu

- **▶ Ollama Run**: Starts the Ollama service process. This function is the same as the "Ollama Run" button on the main interface. The "▶" icon in front indicates start/run.
- **■ Ollama Stop**: Stops the currently running Ollama service process. This function is the same as the "Ollama Stop" button on the main interface. The "■" icon in front indicates stop.
- **Save Log**: Saves the log content displayed in the "Ollama Log Output" area on the right to a text file.
- **Copy Log**: Copies all content from the log area on the right to the system clipboard. This function is the same as the "Copy Log" button on the main interface.
- **Clear Log**: Clears the displayed content in the log area on the right. This function is the same as the "Clear Log" button on the main interface.

#### 3.3 Info Menu

- **Help**: Displays help information for this page.
- **About**: Displays about information. A window will pop up showing the name, version number, developer information, copyright notice, and other details of this Ollama Launcher application.

### 4. System Tray

Right-clicking the system tray icon provides a menu, which is very convenient when minimized to the tray.

- **Show Launcher**: Displays the launcher. Clicking this option will redisplay the previously hidden or minimized Ollama Launcher main window, bringing it to the front of the screen.
- **▶ Ollama Run**: Runs Ollama. Used to start the Ollama service process. This has the same function as the "Ollama Run" button in the main window and the "Ollama Run" option in the "Action" menu.
- **■ Ollama Stop**: Stops Ollama. Used to stop the currently running Ollama service process. This has the same function as the "Ollama Stop" button in the main window and the "Ollama Stop" option in the "Action" menu.
- **Exit**: Exits. Completely closes the Ollama Launcher application. Typically, exiting the launcher also stops the Ollama service process started by it.

### 5. Notifications

The launcher sends notifications through the system notification channel when the Ollama service starts and stops.

1. **Startup Notification**: When `ollama serve` starts, displays the PID (process number) of the started Ollama service along with the current timestamp.
2. **Shutdown Notification**: When `ollama serve` stops for some reason (user operation or abnormal exit), displays the exit code of the Ollama service shutdown along with the current timestamp.

### 6. Pop-up Windows

Some errors that cause significant interruptions are displayed via pop-up windows to provide more noticeable alerts to users.

## Get More Help / Report Issues / Discuss New Features

[GitHub Project Homepage](https://github.com/NGC13009/ollama-launcher.git ) 

Please contact the author or submit an issue if you encounter problems or want to discuss new features. You can open this page in your browser by clicking the button at the bottom of the About page.

'''
