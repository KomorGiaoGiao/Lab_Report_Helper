import subprocess
import tempfile
import os

from langchain.tools import tool


@tool
def run_python(code: str) -> str:
    """执行 Python 代码，用于生成 docx 文件等任务"""
    with tempfile.NamedTemporaryFile(
        suffix=".py", delete=False, mode="w", encoding="utf-8"
    ) as f:
        f.write(code)
        f.flush()
        tmp_path = f.name

    try:
        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return f"执行错误:\n{result.stderr}"
        if result.stdout:
            return result.stdout
        return "执行成功，无输出"
    except subprocess.TimeoutExpired:
        return "错误: 执行超时(30s)"
    finally:
        os.unlink(tmp_path)
