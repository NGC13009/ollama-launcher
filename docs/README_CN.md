# ollama-launcher
更好的ollama启动器，支持更多可设置参数，允许快速启停，以及最小化至系统托盘等.

![title png](./title.png)

快速链接：
[ollama-launcher 下载与发布页](https://github.com/NGC13009/ollama-launcher/releases/)
[ollama zip 版本下载](https://github.com/ollama/ollama/releases/)
[完整说明书](Instructions_CN.md)

## 快速开始

1. 下载 ollama-launcher：[ollama-launcher的直接可执行文件下载链接](https://github.com/NGC13009/ollama-launcher/releases/)

2. 下载 ollama 本体：推荐从[ollama/release](https://github.com/ollama/ollama/releases/)下载zip版本的ollama。

3. 分别解压 ollama-launcher 以及 ollama 到您希望安装的程序路径。（两者一般是不同的路径，例如您可以将ollama-launcher解压安装到`C:/application/ollama/ollama-launcher`，并同时将ollama解压安装到`C:/application/ollama/OLLAMA_FILE/`）

4. 之后，启动ollama-launcher并配置ollama的可执行文件路径。使ollama-launcher可以正确找到ollama并启动它。

5. 完成！可以开始启动一个 ollama 进程，按照需要快速配置，管理ollama的版本并升级等操作了。也可以正常通过api使用其他应用调用ollama进行LLM对话。（例如通过PowerShell或bash执行`ollama run qwen3:0.6b`与大模型对话）

6. 详细说明参考[说明书](Instructions_CN.md)

> 你也可以通过ollama-launcher上方的菜单栏，获取最新版的 ollama zip 的下载链接。
>
> 使用默认安装的ollama也可以，但是您需要手动关闭它的自动启动，并完全由ollama-launcher代理ollama的守护进程。如果不知道怎么做，那么推荐直接下载zip版本。
> 如果您使用ollama setup安装，那么默认路径是：
> 
> ```
> C:\Users\<你的用户名>\AppData\Local\Programs\Ollama\ollama.exe
> ```

## 简介

Ollama Launcher 是 ollama 的启动器，可以方便地启动和管理 ollama 服务进程。

Ollama Launcher 旨在简化配置ollama server的启动参数。免去不断修改环境变量与启动停止守护进程的麻烦。如此一来，修改ollama守护进程的运行参数，启停服务进程将会更加方便。

Ollama Launcher 不能管理模型，即只能启动和停止 ollama 服务进程，不能拉取，运行，配置模型。为了配置模型，你仍旧需要使用命令行或其他程序。

## ⚠ 注意事项

当前程序不支持自动更新，需要手动更新。如果您觉得程序似乎显得有些过时，或者很久没更新过了，那么请转到关于（About）选项卡，查看这个仓库内最新版的程序并下载更新。

默认情况下，使用zip解压的ollama不会自动更新，需要手动检查更新（避免自动更新是最开始我写这个启动器的目的）。

第一次使用前，请配置模型存储路径，重新配置存储路径不会导致模型文件的搬移操作。一旦重设路径，你仍旧需要手动搬移这些模型。

## 获取更多帮助 / 问题反馈 / 新添加功能讨论

[GitHub 项目主页](https://github.com/NGC13009/ollama-launcher.git )

请联系作者或提交issue。你可以通过ollama-launcher的菜单栏：About页面下方的按钮在浏览器打开此页面。


