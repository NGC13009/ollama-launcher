#include <stdio.h>
#include <stdlib.h>
#include <windows.h>

BOOL WINAPI ConsoleHandler(DWORD dwType)
{
    if (dwType == CTRL_C_EVENT)
    {
        printf("\n[INFO] go out...\n");
        exit(0);
    }
    return TRUE;
}

int main(int argc, char *argv[])
{
    SetConsoleCtrlHandler(ConsoleHandler, TRUE);
    printf("Press Ctrl+C to stop the service\n\n");

    // 随便检查个环境变量看看生效没有
    char *tmpdir = getenv("OLLAMA_TMPDIR");
    if (tmpdir)
    {
        printf("[INFO] OLLAMA_TMPDIR is set to: %s\n", tmpdir);
    }
    else
    {
        printf("[WARN] OLLAMA_TMPDIR is not set\n");
    }

    char *tmpdir2 = getenv("OLLAMA_USE_MLOCK");
    if (tmpdir2)
    {
        printf("[INFO] OLLAMA_USE_MLOCK is set to: %s\n", tmpdir2);
    }
    else
    {
        printf("[WARN] OLLAMA_USE_MLOCK is not set\n");
    }

    int count = 0;
    printf("[test] very long line, long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long \n");
    printf("[test color] \x1b[91m[app err ]\t + message + \x1b[0m\n");
    while (1)
    {
        // 显示点什么出去...
        printf("\033[32m[INFO]\033[0m  now %d s.\n", ++count); // 带点颜色测试
        fflush(stdout);
        Sleep(1000); // 等1s
    }

    return 0;
}
