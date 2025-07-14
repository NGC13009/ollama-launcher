# ollama-launcher Full Manual

> This page is translated only from AI, and may not be completely accurate. If you find some expressions strange, please refer to the corresponding content on the Chinese page, and try to understand it using a translator you find more user-friendly. You can also provide feedback on any inaccuracies in the translation. [Chinese instruction page](./Instructions_CN.md)

A better ollama launcher, supporting more configurable parameters, allowing quick start and stop, and minimizing to the system tray.

![title png](./title.png)

## Getting Started

1. Download ollama-launcher: [Direct executable file download link for ollama-launcher](https://github.com/NGC13009/ollama-launcher/releases/)

2. Download ollama itself: It is recommended to download the zip version of ollama from [here](https://github.com/ollama/ollama/releases/).

3. Extract ollama-launcher and ollama to the installation path you want. (The two are generally in different paths, for example, you can extract ollama-launcher to `C:/application/ollama/ollama-launcher`, and extract ollama to `C:/application/ollama/OLLAMA_FILE/`.)

4. Start ollama-launcher and configure the path to the ollama executable file. Make sure ollama-launcher can correctly find and start ollama.

5. Done! You can now start an ollama process, quickly configure, manage ollama versions, and upgrade as needed. You can also normally use other applications to call ollama for LLM conversations through the API. (For example, execute `ollama run qwen3:0.6b` in PowerShell or bash to converse with large models.)

6. For detailed instructions, refer to [Manual](Instructions_CN.md)

> You can also get the latest version of the ollama zip download link through the menu bar above the ollama-launcher.
>
> Using the default installed ollama is also possible, but you need to manually turn off its automatic startup and let ollama-launcher manage the ollama daemon process. If you don't know how to do this, it is recommended to directly download the zip version.
> If you use ollama setup to install, the default path is:
> 
> ```
> C:\Users\<your username>\AppData\Local\Programs\Ollama\ollama.exe
> ```

Ollama Launcher is a launcher for ollama, which can conveniently start and manage the ollama service process.

Ollama Launcher aims to simplify the configuration of the ollama server startup parameters. It avoids the hassle of constantly modifying environment variables and starting and stopping the daemon process. In this way, modifying the runtime parameters of the ollama daemon process, starting and stopping the service process will be more convenient.

Ollama Launcher cannot manage models, that is, it can only start and stop the ollama service process, and cannot pull, run, or configure models. To configure models, you still need to use the command line or other programs.

Due to its simple functionality, ollama-launcher currently only has an English version. In theory, reading the instructions should not affect usage.

The Chinese instructions are accurate, and the English instructions are machine-translated and have not been rigorously reviewed. If you find any problematic areas, you can try submitting a modification (PR).

Since updates may not be timely, the instructions are for reference only and may not be the latest version.

The program provides a manual that can be accessed through the taskbar, allowing you to view the manual content without an internet connection. However, this manual is not carefully formatted and is quite simple. The content is completely the same as the instructions on GitHub.
![brief](./brief.png)

The functions of Ollama Launcher include the following points:
1. Start the ollama service process (`ollama serve`)
2. Stop the ollama service process (`ollama serve`)
3. Configure startup parameters (ollama sets startup parameters through environment variables, such as port, runtime context, and CUDA acceleration devices)
4. Support minimizing to the tray
5. Support starting directly in the background tray
6. Easy access to ollama service logs
7. Avoid ollama upgrade prompts
8. Cross-platform (other platforms besides Windows have not been tested, and you may need to compile it yourself using pyinstaller, and it is not guaranteed to be usable. Generally, if you cannot compile it, it is likely an issue with your Python environment)

Ollama Launcher aims to simplify the management of the Ollama service process. The interface is mainly divided into two areas, left and right, as well as the top menu bar, bottom status bar, and operation buttons.

### 1. Left Area (Configuration Area)

The configuration area is the main configuration area for the Ollama Launcher. Here, you can set various environment variables and startup options to better control the behavior of the Ollama service.

#### 1.1. Environment Variables and Options

At the top: **Ollama Executable Path**: Used to specify the full path to `ollama.exe` (or the corresponding executable file for the operating system). Users can manually enter it in the input box or click the "..." button on the right to browse the file system and select it.

At the bottom: **Checkbox (Auto start ollama & hide to tray on launch)**: When checked, when this Ollama Launcher program is started, it will automatically attempt to start the Ollama service and minimize its window to the system tray area.

#### 1.2. Environment Variables & Options

This is the core configuration area, which lists in a list format various environment variables and startup options that can be passed to the Ollama server. Users can directly modify these values in the corresponding text boxes.

> In the tkinter interface, displaying `×` indicates that the option is selected (True, 1), while if it is empty `  ` it is unselected (False, 0).

1. **OLLAMA_MODELS**: Controls the model storage location. Specifies where Ollama loads and saves downloaded model files to the disk directory.
2. **OLLAMA_TMPDIR**: Controls the temporary file location. Specifies the directory where Ollama stores temporary files during operation (such as when decompressing or converting models).
3. **OLLAMA_HOST**: Controls the network listening configuration. Determines which network interface (IP address) and port number Ollama service binds to receive client requests. This affects the service's accessibility (local access or local network access).
4. **OLLAMA_ORIGINS**: Controls API access permissions (CORS). Sets which sources (domains, IP addresses) of front-end applications are allowed to make cross-origin API calls to Ollama.
5. **OLLAMA_CONTEXT_LENGTH**: Controls the model's processing capability (context window). Sets the maximum number of text tokens the model can understand and generate (context window size).
6. **OLLAMA_KV_CACHE_TYPE**: Controls the model cache precision. Configures the quantization type of Key/Value cache used by the model during inference, affecting memory usage and possibly the balance between performance and accuracy.
7. **OLLAMA_KEEP_ALIVE**: Controls the model's loading duration. Specifies how long a model remains loaded in memory (RAM or VRAM) after it is no longer in use. This affects the response speed when the model is called again and the system resource usage.
8. **OLLAMA_MAX_QUEUE**: Controls the request queue limit. When the server is busy, it determines the maximum number of requests that can be received and placed in the waiting queue for processing. This affects the request processing capability under high concurrency.
9. **OLLAMA_NUM_PARALLEL**: Controls the parallel processing capability. Sets how many inference requests Ollama can process simultaneously. This affects the server's throughput and resource utilization.
10. **OLLAMA_ENABLE_CUDA**: Controls NVIDIA GPU acceleration. Determines whether to enable NVIDIA's CUDA technology to utilize the GPU for computing acceleration.
11. **CUDA_VISIBLE_DEVICES**: Controls the use of NVIDIA GPUs. If the system has multiple NVIDIA GPUs, this variable specifies which one or ones Ollama should use (by index number).
12. **OLLAMA_FLASH_ATTENTION**: Controls a specific optimization technique. Determines whether to enable the FlashAttention algorithm (an optimized method for Transformer attention calculations), which can improve inference speed and reduce memory usage on compatible hardware.
13. **OLLAMA_USE_MLOCK**: Controls memory locking behavior (primarily for Linux/macOS). Determines whether to attempt to lock model data in physical memory (RAM) to prevent the operating system from swapping it to slower disk storage, ensuring performance stability.
14. **OLLAMA_MULTITASK_CACHE**: Controls the multitask caching strategy. Adjusts the caching mechanism related to running multiple models or handling multiple types of tasks, which may affect performance in these scenarios.
15. **OLLAMA_INTEL_GPU**: Controls Intel GPU acceleration. Determines whether to attempt to enable Intel's integrated or discrete graphics for computing acceleration. (Do not check for other graphics cards.)
16. **OLLAMA_DEBUG**: Controls the level of detail in logs. Determines whether Ollama outputs more detailed debug information to logs, which is used for troubleshooting.

These items are environment variables used to configure the behavior of the Ollama server. Changing these values will affect how the Ollama service runs after startup:

#### 1.3. Operation Buttons

Through the operation buttons, you can conveniently start, stop, and manage the Ollama service process. The specific operations are as follows:

- **Ollama Run**: Starts the Ollama service process.
- **Ollama Stop**: Stops the currently running Ollama service process.
- **Copy Log**: Copies all the content in the right log area to the clipboard.
- **Clear Log**: Clears the displayed content in the right log area.
- **Hide to tray**: Minimizes the current launcher window to the system tray area.
- **Bottom status bar**: Displays the status of the most recent operation.

> When closing ollama-launcher, if there are background daemon processes running, it will prompt whether to close all ollama processes and exit, or minimize to the system tray.

### 2. Right Area (Log Output Area)

**Ollama Log Output**: This is a text display area used to show in real-time the startup information, running status, warnings, errors, and operation logs of the Ollama service process. You can see timestamps, log levels ([app info], [app warn], etc.), and specific log content.

### 3. Top Menu Bar

Includes four menu items: **App**, **Action**, **Log**, and **Info**. These are mainly about the management of the application, operations, logs, and information. Some operations in the menu items overlap with the operations on the main interface.

#### 3.1. App Menu

The App menu is used to manage the Ollama daemon process. It mainly includes the following options:

- **Hide to Tray**: Minimizes the Ollama Launcher program window to the system tray area (notification area of the taskbar). This is the same function as the "Hide to tray" button on the main interface.
- **Print Welcome**: Reprints the welcome message displayed when the program starts in the right log output area.
- **Edit additional Environment**: Edit additional environment variables. Allows users to add or modify other Ollama environment variables not displayed by default in the "Environment Variables & Options" list on the main interface, or manage them in a different way.
- **Save Config**: Save the current configuration. Saves all changes you have made on the interface (including the Ollama executable file path, the values of all environment variables, etc.) to a configuration file, so that these settings can be loaded when starting next time. In fact, you don't need to save manually, because the program automatically saves when exiting.
- **Reset Config**: Reset the configuration. Restores all settings to the program's default state or initial configuration file state.
- **Exit**: Exit the Ollama Launcher application.

#### 3.2. Action Menu

Used to start and stop the Ollama daemon process.

- **▶ Ollama Run**: Starts the Ollama service process. This is the same function as the "Ollama Run" button on the main interface. The "▶" icon before it indicates start/run.
- **■ Ollama Stop**: Stops the currently running Ollama service process. This is the same function as the "Ollama Stop" button on the main interface. The "■" icon before it indicates stop.

#### 3.3. Log Menu

This section is for log settings and operations.

- **Enable wrap**: Enable line wrapping. Automatically wraps the content that exceeds the screen width to the next line in the log output, to avoid truncating the log output due to exceeding the screen width.
- **Disable wrap**: Disable line wrapping. The content that exceeds the screen width will not be automatically wrapped to the next line, which can prevent a long content from splitting the log into parts.
- **Save Log**: Save the log. Saves the log content displayed in the "Ollama Log Output" area on the right to a text file.
- **Copy Log**: Copy the log. Copies all the content in the log area on the right to the system clipboard. This is the same function as the "Copy Log" button on the main interface.
- **Clear Log**: Clear the log. Clears the displayed content in the right log area. This is the same function as the "Clear Log" button on the main interface.

#### 3.4. Info Menu

The Info menu provides functions related to information about the Ollama Launcher program and system information, including the following content:

- **Ollama webpage**: Opens the Ollama official website, where you can browse the latest information, documentation, and community support for Ollama.
- **Ollama model list**: Displays the list of available Ollama models, helping users understand the types of models currently supported.
- **Download Ollama**: Provides a link to download the Ollama zip file, making it convenient for users to install the latest version.
- **Open Ollama path**: Opens the installation directory of Ollama, making it convenient for users to view or customize configuration files.
- **System info**: Displays information about the current system, such as the operating system version, helping users understand the runtime environment.
- **Ollama version**: Displays the version number of the current Ollama, making it convenient for users to confirm whether it is the latest version.
- **Help**: Displays the help information for this page. Helps users understand how to use the various functions of the Ollama Launcher.
- **About**: Displays the about information. If you need to update the ollama-launcher, you can quickly navigate to the GitHub page from here.

### 4. System Tray

Right-clicking on the system tray provides a menu, which is very convenient when the program is minimized to the tray.

- **Show Launcher**: Show the launcher. Clicking this option will bring back the previously hidden or minimized Ollama Launcher main window and display it on the screen in front.
- **▶ Ollama Run**: Run Ollama. Used to start the Ollama service process. This is the same function as the "Ollama Run" button on the main interface and the "Ollama Run" option in the "Action" menu.
- **■ Ollama Stop**: Stop Ollama. Used to stop the currently running Ollama service process. This is the same function as the "Ollama Stop" button on the main interface and the "Ollama Stop" option in the "Action" menu.
- **Exit**: Exit. Completely closes the Ollama Launcher application. Normally, exiting the launcher will also stop the Ollama service process it started.

### 5. Notifications

The launcher sends notifications through the system notification channel when the Ollama service starts and stops.

1. **Start Notification**: When `ollama serve` starts, it displays the PID (process ID) of the running Ollama service and the current timestamp.
2. **Stop Notification**: When `ollama serve` stops due to some reason (user operation or abnormal exit), it displays the exit code of the Ollama service and the current timestamp.

### 6. Pop-up Windows

Some errors will cause interruptions that cannot be ignored, and these messages are designed to be displayed through pop-up windows to alert users with more prominent messages.

## ⚠ Notes

The current program does not support automatic updates, and updates must be done manually. If you feel that the program seems somewhat outdated, or has not been updated for a long time, please go to the "About" tab and check the latest version of the program in this repository to download and update.

By default, the Ollama version extracted from the zip file will not automatically update, and manual checks for updates are required (avoiding automatic updates was one of the main reasons I created this launcher).

Before the first use, please configure the model storage path. Resetting the storage path will not automatically move the model files. Once the path is reset, you will still need to manually move these models.

## Get More Help / Feedback on Issues / Discussion for New Features

[GitHub Project Homepage](https://github.com/NGC13009/ollama-launcher.git )

Please contact the author or submit an issue. You can access this page in your browser via the button below the About page in the menu bar of ollama-launcher.


