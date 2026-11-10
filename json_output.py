from json_tool import JSON_OUTPUT_TOOL
from llm import MODEL, LLMError, chat, client, usage

SYSTEM_PROMPT = (
    "把用户输入解析为 JSON。字段要求："
    "title 是字符串，tags 是字符串数组，score 是分数。\n"
    "示例输入：这个大型3A游戏GTA5在平台上的评分是5分\n"
    "示例输出："
    '{"title": "GTA5", "tags": ["3A"], "score": 5}'
)


def show(piece: str) -> None:
    print(piece, end="", flush=True)


def main() -> None:
    while True:
        try:
            q = input("\n你 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not q:
            continue
        if q in ("/exit", "exit"):
            break
        if q == "/cost":
            print(usage.summary())
            continue

        r = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": q},  # ← 只要 system + user
            ],
            tools=[JSON_OUTPUT_TOOL],
            extra_body={"thinking": {"type": "disabled"}},
            tool_choice={"type": "function", "function": {"name": "save_game"}},
        )

        msg = r.choices[0].message
        if not msg.tool_calls:  # ← 防御：万一还是没调
            print(f"[未调用工具] {msg.content}")
            continue

        print(msg.tool_calls[0].function.arguments)


if __name__ == "__main__":
    main()
