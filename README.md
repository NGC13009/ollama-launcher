# ollama-launcher
A better Ollama launcher with support for more configurable parameters, allowing quick start/stop and minimization to the system tray.

中文说明：[点此进入中文说明](docs/README_CN.md)

![title png](./docs/title.png)

Quick Links:
[ollama-launcher Download and Release Page](https://github.com/NGC13009/ollama-launcher/releases/)
[ollama zip version download](https://github.com/ollama/ollama/releases/)
[Full Instructions](docs/Instructions_CN.md)

## Quick start

1. Download ollama-launcher: [Direct executable file download link for ollama-launcher](https://github.com/NGC13009/ollama-launcher/releases/)

2. Download the ollama main program: It is recommended to download the zip version of ollama from [ollama/release](https://github.com/ollama/ollama/releases/).

3. Extract both ollama-launcher and ollama to the installation path of your choice. (They are generally placed in different paths. For example, you can extract and install ollama-launcher to `C:/application/ollama/ollama-launcher` and simultaneously extract and install ollama to `C:/application/ollama/OLLAMA_FILE/`.)

4. After that, launch ollama-launcher and configure the path to the ollama executable file. This allows ollama-launcher to correctly locate and start ollama.

5. Done! You can now start an ollama process, quickly configure it as needed, manage ollama versions, and perform upgrades. You can also normally use other applications to call ollama for LLM conversations via the API. (For example, execute `ollama run qwen3:0.6b` in PowerShell or bash to converse with large models.)

6. For detailed instructions, refer to the [User Manual](docs/Instructions_CN.md)

> You can also obtain the download link for the latest ollama zip file via the menu bar above the ollama-launcher.
>
> Using the default installed ollama is also possible, but you need to manually disable its auto-start and let ollama-launcher fully manage the ollama daemon process. If you are unsure how to do this, it is recommended to directly download the zip version.
> If you installed ollama using the setup, the default path is:
>
> ```
> C:\Users\<Your Username>\AppData\Local\Programs\Ollama\ollama.exe
> ```

## Introduction

Ollama Launcher is a launcher for ollama, allowing you to conveniently start and manage the ollama service process.

Ollama Launcher aims to simplify the configuration of ollama server startup parameters. It eliminates the need to constantly modify environment variables and start/stop the daemon process. As a result, modifying the runtime parameters of the ollama daemon process, as well as starting and stopping the service process, will be much more convenient.

Ollama Launcher cannot manage models. That is, it can only start and stop the ollama service process, and cannot pull, run, or configure models. To configure models, you still need to use the command line or other programs.

## ⚠ Notes

The current program does not support automatic updates and requires manual updates. If you feel that the program seems somewhat outdated or has not been updated for a long time, please go to the "About" tab and check for the latest version of the program in this repository to download and update.

By default, the ollama version extracted from the zip file does not automatically update, and manual checks for updates are required (avoiding automatic updates was one of the main reasons I created this launcher).

Before using it for the first time, please configure the model storage path. Changing the storage path again will not cause the model files to be moved. Once the path is reset, you will still need to manually move these models.

## Get More Help / Feedback / Discussion for New Features

[GitHub Project Homepage](https://github.com/NGC13009/ollama-launcher.git)

Please contact the author or submit an issue. You can access this page in your browser via the button below the About page in the menu bar of ollama-launcher.


