# Lab Report Agent

## Architecture
- **单 Agent + 五工具**（web_search, run_python, run_command, read_file, write_file）
- Agent 自己写 Python 脚本生成 docx
- 流式输出，实时显示工具调用和 Markdown

## Tools
- web_search: Exa MCP（`https://mcp.exa.ai/mcp`，无需 key）
- run_python: 写临时文件 → subprocess 执行 Python
- run_command: subprocess 执行 PowerShell
- read_file: 读文件（支持 txt/pdf/xlsx）
- write_file: 写文件

## Key Decisions
- 单 Agent（去掉 handoff，简化架构）
- TUI 用 Textual（独立输入区 + Markdown 渲染）
- .env 文件管理 API Key
- 首次运行有配置引导

## User
- CS 背景，学习 AI Agent
- 偏好中文交流，代码示例 + C++ 类比
- DeepSeek V4 Flash（thinking disabled），LangChain 1.3.1
