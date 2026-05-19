import subprocess

from langchain.tools import tool


@tool
def run_command(command: str) -> str:
    """执行 PowerShell 命令（相当于 opencode 的 bash 工具）"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            return f"错误:\n{result.stderr}"
        return result.stdout or "执行成功，无输出"
    except subprocess.TimeoutExpired:
        return "错误: 执行超时(60s)"
    except FileNotFoundError:
        return "错误: 找不到 powershell，当前系统不是 Windows"
    except Exception as e:
        return f"错误: {e}"
