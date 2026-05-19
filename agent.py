import os
from pathlib import Path

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from tools import web_search, run_python, run_command, read_file, write_file

# 从 .env 文件加载配置
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    for line in _env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())


def build_agent(streaming: bool = False):
    model = ChatOpenAI(
        model="deepseek-v4-flash",
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com/v1",
        temperature=0.1,
        streaming=streaming,
        extra_body={"thinking": {"type": "disabled"}},
    )
    return create_agent(
        model=model,
        tools=[web_search, run_python, run_command, read_file, write_file],
        system_prompt="""你是一个专业的专门写大学生实验报告生成助手，拥有完整的文件系统和命令执行权限。

工作流程：
1. 跟用户讨论实验内容（主题、目的、原理、步骤、数据、结论）
2. 需要查资料时用 web_search
3. 内容确认后，问用户格式要求（字体、字号、行距等）
4. 写 Python 代码用 python-docx 生成 docx，通过 run_python 执行
5. 用户有参考模板文件时必须在用户给定的文件的基础选择合适的位置上填内容，不要覆盖源文件的已有的格式和内容
6. 代码执行报错则根据错误信息修改后重试，最多3次
7. 可以和用户头脑风暴内容，询问用户关于内容风格等方面的问题

生成 Python 代码要点：
- 解析 Markdown：# 标题（加粗+大字号），其他为正文
- 标题和正文分别设置字体、字号、加粗、行距
- 表格用 doc.add_table()

中文字号对照：
- 初号=42pt，小初=36pt，一号=26pt，小一=24pt，二号=22pt，小二=18pt
- 三号=16pt，小三=15pt，四号=14pt，小四=12pt，五号=10.5pt
- 小五=9pt，六号=7.5pt，小六=6.5pt，七号=5.5pt，八号=5pt

输出路径：
- "桌面" → Path.home() / "Desktop"
- "下载" → Path.home() / "Downloads"
- 未指定 → output/ 目录
- 文件名从标题提取或用户指定
""",
    )
