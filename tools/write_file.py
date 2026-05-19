from langchain.tools import tool


@tool
def write_file(path: str, content: str) -> str:
    """写入文件内容（相当于 opencode 的 write 工具）"""
    import os

    path = os.path.abspath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"文件已保存: {path}"
    except Exception as e:
        return f"错误: 写入失败 - {e}"
