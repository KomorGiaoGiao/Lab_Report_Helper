"""TUI 入口，包含首次使用的配置引导"""

import os
import sys
import threading
from pathlib import Path

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import Header, Input, Static, Button
from textual.screen import Screen
from rich.text import Text
from rich.markdown import Markdown
from langchain_core.callbacks import BaseCallbackHandler

from agent import build_agent

CODE_THEME = "monokai"
ENV_PATH = Path(_root) / ".env"


# ──────────────────────────────────────────────
# 配置检查
# ──────────────────────────────────────────────

def is_configured():
    key = os.environ.get("DEEPSEEK_API_KEY")
    if key:
        return True
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("DEEPSEEK_API_KEY="):
                return True
    return False


def save_key_to_env(key: str):
    lines = []
    found = False
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("DEEPSEEK_API_KEY="):
                lines.append(f"DEEPSEEK_API_KEY={key}")
                found = True
            else:
                lines.append(line)
    if not found:
        lines.append(f"DEEPSEEK_API_KEY={key}")
    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ──────────────────────────────────────────────
# 配置引导界面
# ──────────────────────────────────────────────

class ConfigScreen(Screen):
    def compose(self):
        yield Static("", id="spacer")
        yield Static(
            Text.assemble(
                ("实验报告生成助手\n", "bold cyan"),
                ("─" * 30, "dim"),
                ("\n\n首次使用需要配置 API Key\n", "bold"),
                ("\n1. 在 https://platform.deepseek.com 注册获取 Key\n", ""),
                ("2. 输入 Key 并按回车即可保存\n\n", "dim"),
            ),
            id="help",
        )
        yield Input(placeholder="输入 DeepSeek API Key...", id="key_input", password=True)
        yield Static("", id="status")

    def on_input_submitted(self, event: Input.Submitted):
        key = event.value.strip()
        if not key:
            return
        save_key_to_env(key)
        os.environ["DEEPSEEK_API_KEY"] = key
        self.dismiss(True)


# ──────────────────────────────────────────────
# 聊天界面
# ──────────────────────────────────────────────

class StreamHandler(BaseCallbackHandler):
    def __init__(self, on_token, on_tool, on_done):
        self.on_token = on_token
        self.on_tool = on_tool
        self.on_done = on_done
        self.buffer = ""

    def on_tool_start(self, serialized, input_str, **kwargs):
        self.on_tool(serialized.get("name", "tool"))

    def on_tool_end(self, output, **kwargs):
        out = str(output).strip()
        if out:
            self.on_tool("", out[:200])

    def on_llm_new_token(self, token, **kwargs):
        self.buffer += token
        self.on_token(self.buffer)


class ChatScreen(Screen):
    agent = None
    messages = []
    _stream_widget = None
    _stream_seq = 0

    def compose(self):
        yield Header(show_clock=False)
        yield VerticalScroll(id="chat")
        yield Input(placeholder="输入消息...", id="input")

    def on_mount(self):
        self.agent = build_agent(streaming=True)
        self._ask("你好")

    def on_input_submitted(self, event: Input.Submitted):
        text = event.value.strip()
        if not text:
            return
        self.query_one("#input", Input).value = ""
        if text.lower() in ("quit", "exit"):
            self.app.exit()
            return
        if text.lower() == "/config":
            self.app.push_screen("config", self._on_config_done)
            return
        if text.lower() in ("/help", "/h"):
            chat = self.query_one("#chat", VerticalScroll)
            chat.mount(Static(Text("/config  更换 API Key\n/clear  清屏\nquit     退出", style="dim")))
            chat.scroll_end(animate=False)
            return
        if text.lower() in ("/clear", "/cls"):
            chat = self.query_one("#chat", VerticalScroll)
            chat.remove_children()
            return
        self._show_user(text)
        self._ask(text)

    def _on_config_done(self, changed):
        if changed:
            self.agent = build_agent(streaming=True)

    def _show_user(self, text):
        chat = self.query_one("#chat", VerticalScroll)
        chat.mount(Static(Text(f"\n> {text}", style="bold green")))
        chat.scroll_end(animate=False)

    def _show_tool(self, name, output="", seq=None):
        if seq is not None and seq != self._stream_seq:
            return
        chat = self.query_one("#chat", VerticalScroll)
        chat.mount(Static(Text(f"  > {name}", style="bold yellow")))
        if output:
            chat.mount(Static(Text(f"  -> {output}", style="dim")))
        chat.scroll_end(animate=False)

    def _stream_response(self, text, seq=None):
        if seq is not None and seq != self._stream_seq:
            return
        if self._stream_widget is not None:
            self._stream_widget.update(Markdown(text, code_theme=CODE_THEME))
        self.query_one("#chat", VerticalScroll).scroll_end(animate=False)

    def _ask(self, text):
        self._stream_seq += 1
        seq = self._stream_seq
        self.messages.append({"role": "user", "content": text})
        msgs = list(self.messages)
        chat = self.query_one("#chat", VerticalScroll)
        md = Markdown("", code_theme=CODE_THEME)
        self._stream_widget = Static(md)
        chat.mount(self._stream_widget)
        chat.scroll_end(animate=False)

        def on_token(t):
            self.app.call_from_thread(self._stream_response, t, seq)

        def on_tool(name, output=""):
            self.app.call_from_thread(self._show_tool, name, output, seq)

        handler = StreamHandler(on_token, on_tool, lambda: None)

        def task():
            try:
                result = self.agent.invoke(
                    {"messages": msgs},
                    config={"callbacks": [handler]},
                )
                self.messages.append(result["messages"][-1])
            except Exception as e:
                self.app.call_from_thread(lambda: self._stream_response(f"\n**错误:** {e}", seq))
            finally:
                self.app.call_from_thread(lambda: self._finish_stream(seq))

        threading.Thread(target=task, daemon=True).start()

    def _finish_stream(self, seq):
        if seq == self._stream_seq:
            self._stream_widget = None


# ──────────────────────────────────────────────
# 主应用
# ──────────────────────────────────────────────

class LabReportApp(App):
    TITLE = "实验报告生成助手"
    CSS = """
    Screen {
        background: #1e1e1e;
    }
    Header {
        background: #2d2d2d;
        color: #64B5F6;
        text-style: bold;
    }
    #chat {
        height: 1fr;
        padding: 1;
    }
    #input {
        dock: bottom;
        margin: 1;
    }
    Static {
        margin: 0 1;
    }
    #help {
        padding: 2 4;
    }
    #key_input {
        margin: 1 4;
    }
    #status {
        height: 3;
    }
    """

    SCREENS = {
        "config": ConfigScreen,
        "chat": ChatScreen,
    }

    def on_mount(self):
        if is_configured():
            self.push_screen("chat")
        else:
            self.push_screen("config", self._on_config_done)

    def _on_config_done(self, configured):
        if configured:
            self.push_screen("chat")


def main():
    app = LabReportApp()
    app.run()


if __name__ == "__main__":
    main()
