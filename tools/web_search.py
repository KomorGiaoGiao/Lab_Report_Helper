from langchain.tools import tool


@tool
def web_search(query: str) -> str:
    """搜索互联网获取实时信息"""
    import httpx

    try:
        with httpx.Client(timeout=20) as client:
            resp = client.post(
                "https://mcp.exa.ai/mcp",
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "web_search_exa",
                        "arguments": {"query": query},
                    },
                    "id": 1,
                },
                headers={
                    "Accept": "application/json, text/event-stream",
                    "Content-Type": "application/json",
                },
            )
    except Exception as e:
        return f"搜索失败: {e}"

    # 解析 SSE 格式的响应
    body = resp.text
    for line in body.splitlines():
        if line.startswith("data:"):
            import json
            try:
                data = json.loads(line[5:].strip())
            except json.JSONDecodeError:
                continue
            if "error" in data:
                return f"搜索失败: {data['error']}"
            if "result" in data:
                texts = []
                for item in data["result"].get("content", []):
                    if item.get("type") == "text":
                        texts.append(item["text"])
                return "\n\n".join(texts) if texts else "未找到结果"

    return "未找到结果"
