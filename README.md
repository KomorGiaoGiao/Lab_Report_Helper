# 实验报告生成助手

基于 LangChain 的实验报告自动生成 CLI 工具。Agent 自动写 Python 代码用 python-docx 生成格式规范的 docx 文件。

## 功能

- 联网搜索查资料
- 跟用户讨论确定实验内容
- 按用户要求自定义格式（字体、字号、行距等）
- 支持表格、代码块
- 输出 docx 文件
- 完整的文件系统权限（读/写/执行命令）
- 支持 PDF/Excel 等格式读取
- 流式输出，实时显示工具调用

## 安装

```bash
pip install -r requirements.txt
pip install -e .
```

## 使用

```bash
lab-report
```

首次运行会自动引导配置 API Key（需要 [DeepSeek API Key](https://platform.deepseek.com)）。

## 依赖

- langchain + langchain-openai
- python-docx
- rich + textual（TUI）
- httpx（Exa MCP 搜索）
- pypdf、openpyxl（PDF/Excel 读取）

## 项目结构

```
lab-report-agent/
├── agent.py          # Agent 创建（共享）
├── cli/cli_tui.py    # TUI 界面
├── tools/            # 工具实现
│   ├── web_search.py     # Exa MCP 搜索
│   ├── run_python.py     # 执行 Python
│   ├── run_command.py    # 执行 PowerShell
│   ├── read_file.py      # 读文件
│   └── write_file.py     # 写文件
├── .env              # API Key 配置
└── pyproject.toml    # 打包配置
```
