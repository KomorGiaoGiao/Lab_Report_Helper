# 实验报告生成 Agent 架构设计

## 架构：单 Agent + 三工具

```
用户 → Agent（web_search, read_template, run_python）→ docx
```

## Agent 定义

```python
agent = create_agent(
    model=model,
    tools=[web_search, read_template, run_python],
    system_prompt="..."
)
```

### System Prompt 要点
- 工作流：讨论内容 → 确认 → 问格式 → 写 Python 代码 → 执行 → 输出
- 中文字号对照表（三号=16pt 等）
- 输出路径规则（桌面/下载/自定义）
- 代码报错自动重试（最多3次）

## 工具

### web_search
- MCP 连接 Exa（`https://mcp.exa.ai/mcp`）
- 解析 SSE 格式响应

### read_template
- python-docx 读取参考 docx 样式
- 返回字体、字号、加粗、对齐等信息

### run_python
- 写入临时文件 → subprocess 执行
- 超时30秒
- 返回 stdout/stderr

## 工作流

```
用户: "重力加速度实验报告，标题黑体三号..."
  ↓ Agent 生成 Markdown 内容
用户: "确认"
  ↓ Agent 问格式要求（如未指定）
用户: "桌面，宋体五号"
  ↓ Agent 写 Python → run_python → docx
用户: "内容改一下"
  ↓ Agent 修改内容 → 再次生成
```
