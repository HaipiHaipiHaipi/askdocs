from getdoc import retrieve
from llm import chat

DOC_PATH = "docs/sample.md"
SYSTEM_PROMPT = (
    "只依据用户提供的文档回答。文档里没有的，明确说「文档未提及」，不要用常识补充。"
)

QUESTIONS = [
    # ── 有答案的（7 题）──
    "流式输出时，草稿首字和回答首字分别是多少？",
    "流式模式和非流式模式下，返回对象的 object 字段分别是什么值？",
    "流式默认的 usage 是什么？要拿到它需要加什么参数？",
    ".env 和 PowerShell 读取环境变量是什么关系？",
    "API Key 泄露之后该怎么处理？",
    "HTTP 400 和 401 分别代表什么错误？",
    "模型名写错时返回的是什么状态码？",
    # ── 陷阱题（3 题）──
    "reasoning_effort 的 low / high / max 三档，准确率和成本差多少？",  # 提到但没答案
    "这个项目怎么部署到服务器？",  # 完全无关
    "怎么用 tiktoken 精确计算 token 数？",  # 完全无关
]

doc_text = retrieve(DOC_PATH)

for i, q in enumerate(QUESTIONS, 1):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"【文档】\n{doc_text}\n\n【问题】\n{q}"},
    ]
    print(f"\n{'=' * 60}\n[{i}] {q}\n{'=' * 60}")
    chat(messages, on_delta=lambda s: print(s, end="", flush=True))
    print()
