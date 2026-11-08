import os
from dataclasses import dataclass
from typing import Callable

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, OpenAI

load_dotenv(override=True)
MODEL = os.getenv("ASK_MODEL", "deepseek-flash")
TEMPERATURE = float(os.getenv("ASK_TEMPERATURE", "0"))
THINKING = os.getenv("ASK_THINKING", "disabled")
PRICES = {
    "deepseek-flash": (1.0, 4.0),
    "deepseek-v4-pro": (4.5, 13.5),
}
PRICE_IN, PRICE_OUT = PRICES.get(MODEL, (1.0, 4.0))
SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search_docs",
        "description": "在本地技术文档中搜索与问题相关的段落。当你不确定答案时调用。",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "搜索关键词"}},
            "required": ["query"],
        },
    },
}
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)


@dataclass
class Usage:
    calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    reasoning_tokens: int = 0

    def add(self, u) -> None:
        self.calls += 1
        self.prompt_tokens += u.prompt_tokens or 0
        self.completion_tokens += u.completion_tokens or 0
        d = getattr(u, "completion_tokens_details", None)
        if d:
            self.reasoning_tokens += getattr(d, "reasoning_tokens", 0) or 0

    @property
    def cost(self) -> float:
        return (
            self.prompt_tokens * PRICE_IN + self.completion_tokens * PRICE_OUT
        ) / 1_000_000

    def summary(self) -> str:
        if self.calls == 0:
            return "还没调用过模型。"
        return (
            f"调用 {self.calls} 次 | "
            f"输入 {self.prompt_tokens:,} + 输出 {self.completion_tokens:,} token"
            f" | 约 ¥{self.cost:.4f}"
        )


class LLMError(Exception):
    def __init__(self, mes):
        super().__init__(mes)


usage = Usage()


def chat(
    messages: list[dict], on_delta: Callable[[str], None] | None = None, tools=None
) -> str:
    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            stream=True,
            stream_options={"include_usage": True},
            temperature=TEMPERATURE,
            extra_body={"thinking": {"type": THINKING}},
        )
    except APIConnectionError:
        raise LLMError("连不上服务器，检查网络或代理") from None
    except APIStatusError as e:
        if e.status_code == 401:
            raise LLMError("认证失败，检查 .env 里的 DEEPSEEK_API_KEY") from None
        if e.status_code == 402:
            raise LLMError("余额不足，去 platform.deepseek.com 充值") from None
        if e.status_code == 429:
            raise LLMError("请求太频繁，等几秒再试") from None
        if e.status_code >= 500:
            raise LLMError("服务端故障，稍后重试") from None
        raise LLMError(f"请求被拒绝（HTTP {e.status_code}）") from None

    ans: list[str] = []
    for chunk in r:
        if chunk.usage:
            usage.add(chunk.usage)
        if not chunk.choices:
            continue
        content = chunk.choices[0].delta.content
        if content:
            ans.append(content)
            # print(ans)
            if on_delta:
                on_delta(content)
    return "".join(ans)
