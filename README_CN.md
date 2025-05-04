# ollama-launcher
更好的ollama服务启动器

![title png](./title.png)

欢迎使用 Ollama Launcher！

- Ollama Launcher 是 ollama 的启动器，可以方便地启动和管理 ollama 服务进程。
- Ollama Launcher 旨在简化配置ollama server的启动参数。免去不断修改环境变量与启动停止守护进程的麻烦。如此一来，修改ollama守护进程的运行参数，启停服务进程将会更加方便。
- Ollama Launcher 不能管理模型，即只能启动和停止 ollama 服务进程，不能拉取，运行，配置模型。为了配置模型，你仍旧需要使用命令行。

## 使用须知

1. 该程序由Gemini2.5pro生成，目前未经过严格测试。
2. 下面的功能说明也是AI生成的，作者并未严格审核内容，只是大概看了一眼。
3. 由于工作量原因，暂时没有中文版。（不过这几个单词也没啥难看懂的吧，何况这里有一个说明）
4. 中文说明是准确的，英文说明是机翻的，没有严格审查内容，不承诺准确性。

## 功能说明

Ollama Launcher 的功能包括以下几点：
1. 启动 ollama 服务进程（ollama serve）
2. 停止 ollama 服务进程（ollama serve）
3. 配置启动参数（ollama通过环境变量设置启动参数，如端口、运行上下文，运行的CUDA加速设备）
4. 支持最小化到托盘
5. 支持启动后直接进入后台托盘
6. 方便的查看ollama服务运行日志
7. 避免ollama升级提示（坏处是需要手动更新了）
8. 跨平台（除了Windows，其他平台没测试过，需要自行使用pyinstaller编译）

## 使用提示

Ollama 启动器旨在简化 Ollama 服务进程的管理。界面主要分为左右两个区域，以及顶部的菜单栏、底部的状态栏和操作按钮。

### 1. 左侧区域 (配置区)

#### 1.1. 环境变量与选项

最上方的：Ollama Executable Path: 用于指定 ollama.exe（或对应操作系统的可执行文件）所在的完整路径。用户可以通过输入框手动输入，或点击右侧的 "..." 按钮浏览文件系统来选择。
最下方的：复选框 (Auto start ollama & hide to tray on launch): 勾选后，当启动这个 Ollama Launcher 程序时，它会自动尝试启动 Ollama 服务，并将自身窗口最小化到系统托盘区。

#### 1.2. Environment Variables & Options

这是核心配置区域，以列表形式展示了可以传递给 Ollama 服务器的各种环境变量和启动选项。用户可以直接在对应的文本框中修改这些值。

1.    OLLAMA_MODELS: 控制 模型存储位置。指定 Ollama 从哪里加载以及将下载的模型文件保存到哪个磁盘目录。
2.    OLLAMA_TMPDIR: 控制 临时文件位置。指定 Ollama 在运行过程中（如模型解压、转换时）存放临时文件的目录。
3.    OLLAMA_HOST: 控制 网络监听配置。决定 Ollama 服务绑定到哪个网络接口（IP 地址）以及使用哪个端口号来接收客户端的请求。这影响了服务的可访问性（本机访问还是局域网访问）。
4.    OLLAMA_ORIGINS: 控制 API 访问权限 (CORS)。设置允许哪些来源（域名、IP地址）的前端应用跨域调用 Ollama 的 API 接口。这是浏览器的安全策略控制。
5.    OLLAMA_CONTEXT_LENGTH: 控制 模型处理能力 (上下文窗口)。设定模型能够理解和生成的最大文本长度（上下文窗口大小），以 token 数量衡量。
6.    OLLAMA_KV_CACHE_TYPE: 控制 模型缓存精度。配置模型在推理时使用的 Key/Value 缓存的量化类型，影响内存占用和可能的性能/精度平衡。
7.    OLLAMA_KEEP_ALIVE: 控制 模型加载时长。指定一个模型在没有被使用后，在内存（RAM 或 VRAM）中保持加载状态多长时间。影响再次调用该模型时的响应速度和系统资源占用。
8.    OLLAMA_MAX_QUEUE: 控制 请求排队上限。当服务器繁忙时，能接收并放入等待队列处理的最大请求数量。影响高并发下的请求处理能力。
9.    OLLAMA_NUM_PARALLEL: 控制 并行处理能力。设置 Ollama 可以同时处理多少个推理请求。影响服务器的吞吐量和资源利用率。
10.   OLLAMA_ENABLE_CUDA: 控制 NVIDIA GPU 加速。决定是否启用 NVIDIA 的 CUDA 技术来利用 GPU 进行计算加速。
11.   CUDA_VISIBLE_DEVICES: 控制 使用的 NVIDIA GPU。如果系统有多块 NVIDIA GPU，这个变量指定 Ollama 应该使用哪一块或哪几块 GPU（通过索引号）。
12.   OLLAMA_FLASH_ATTENTION: 控制 特定优化技术。决定是否启用 FlashAttention 算法（一种优化 Transformer 注意力计算的方法），可以在兼容的硬件上提升推理速度并减少显存占用。
13.   OLLAMA_USE_MLOCK: 控制 内存锁定行为 (主要用于 Linux/macOS)。决定是否尝试将模型数据锁定在物理内存（RAM）中，防止操作系统将其交换到速度较慢的硬盘上，以保证性能稳定性。
14.   OLLAMA_MULTITASK_CACHE: 控制 多任务缓存策略。调整与同时运行多个模型或处理多类型任务相关的缓存机制，可能影响这些场景下的性能。
15.   OLLAMA_INTEL_GPU: 控制 Intel GPU 加速。决定是否尝试启用 Intel 的集成显卡或独立显卡进行计算加速。
16.   OLLAMA_DEBUG: 控制 日志详细程度。决定 Ollama 是否输出更详细的调试信息到日志中，用于问题排查。

这些项目是用来配置 Ollama 服务器行为的环境变量。修改这些值会影响 Ollama 服务启动后的运行方式：

#### 1.3. 操作按钮

- Ollama Run: 启动 Ollama 服务进程。
- Ollama Stop: 停止当前正在运行的 Ollama 服务进程。
- Copy Log: 复制右侧日志区域的全部内容到剪贴板。
- Clear Log: 清空右侧日志区域显示的内容。
- Hide to tray: 将当前启动器窗口最小化到系统托盘区。
- 底部状态栏：显示最近一次的操作状态。

### 2. 右侧区域 (日志输出区)

Ollama Log Output: 这是一个文本显示区域，用于实时展示 Ollama 服务进程的启动信息、运行状态、警告、错误以及该启动器本身的操作日志。可以看到时间戳、日志级别（[app info], [app warn] 等）和具体的日志内容。

### 3. 顶部菜单栏

包含 "App", "Action", "Info" 三个菜单项。

#### 3.1. App 菜单

- Hide to Tray: 将 Ollama Launcher 程序的窗口最小化到系统托盘区（任务栏通知区域）。这和主界面上的 "Hide to tray" 按钮功能相同。
- Print Welcome: 在右侧的日志输出区域重新打印程序启动时的欢迎信息。
- Edit additional Environment: 编辑额外的环境变量。允许用户添加或修改一些没有在主界面“Environment Variables & Options”列表中默认显示的其他 Ollama 环境变量，或者是以不同方式管理它们。
- Save Config: 保存当前的配置。将你在界面上做的所有更改（包括 Ollama 可执行文件路径、所有环境变量的值等）保存到配置文件中（就是状态栏提到的 config.json），以便下次启动时加载这些设置。其实不用手动保存，因为程序退出时是自动- 保存的。
- Reset Config: 重置配置。将所有设置恢复到程序的默认状态或初始配置文件状态。
- Exit: 退出 Ollama Launcher 应用程序。

#### 3.2. Action 菜单

- ▶ Ollama Run: 启动 Ollama 服务进程。这和主界面上的 "Ollama Run" 按钮功能相同，前面的 "▶" 图标表示启动/运行。
- ■ Ollama Stop: 停止当前正在运行的 Ollama 服务进程。这和主界面上的 "Ollama Stop" 按钮功能相同，前面的 "■" 图标表示停止。
- Save Log: 保存日志。将右侧“Ollama Log Output”区域显示的日志内容保存到一个文本文件中。
- Copy Log: 复制日志。将右侧日志区域的全部内容复制到系统剪贴板。这和主界面上的 "Copy Log" 按钮功能相同。
- Clear Log: 清除日志。清空右侧日志区域显示的内容。这和主界面上的 "Clear Log" 按钮功能相同。

#### 3.3. Info 菜单

- Help: 显示此页面的帮助信息。
- About: 显示关于信息。会弹出一个窗口，显示这个 Ollama Launcher 程序的名称、版本号、开发者信息、版权声明等。

### 4. 系统托盘

右键系统托盘可获取一个菜单，这在最小化到托盘时操作将很方便。

- Show Launcher: 显示启动器。点击这个选项会将之前隐藏或最小化到托盘的 Ollama Launcher 主窗口重新显示出来，放到屏幕最前面。
- ▶ Ollama Run: 运行 Ollama。用于启动 Ollama 服务进程。这和主窗口中的 "Ollama Run" 按钮以及 "Action" 菜单里的 "Ollama Run" 功能相同。
- ■ Ollama Stop: 停止 Ollama。用于停止当前正在运行的 Ollama 服务进程。这和主窗口中的 "Ollama Stop" 按钮以及 "Action" 菜单里的 "Ollama Stop" 功能相同。
- Exit: 退出。完全关闭 Ollama Launcher 这个应用程序。通常情况下，退出启动器也会停止由它启动的 Ollama 服务进程。

### 5. 通知

启动器在ollama服务启动和停止的时候会通过系统通知渠道发送提示。

1. 启动提示：ollama serve 启动时，展示启动的ollama服务 PID 进程号信息，以及当前时间戳。
2. 停止提示：ollama serve 由于一些原因（用户操作或者异常退出）导致停止时，显示ollama服务的停止退出代码以及当前时间戳。

### 6. 弹出窗口

一些错误会导致不可忽略的中断，这些信息被设计为通过弹出窗口提示，以更加醒目的消息提醒用户。

## 获取更多帮助 / 问题反馈 / 新添加功能讨论

GitHub 项目主页: https://github.com/NGC13009/ollama-launcher.git（此页面）

请联系作者或提交issue。你可以通过About页面下方的按钮在浏览器打开此页面。


