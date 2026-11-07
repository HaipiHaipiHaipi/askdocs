from getdoc import pick_blocks, retrieve
from llm import LLMError, chat, usage

SYSTEM_PROMPT = (
    "只依据用户提供的文档回答。文档里没有的，明确说「文档未提及」，不要用常识补充。"
)
DOC_PATH = "docs-vue/src/api/reactivity-core.md"


def show(piece: str) -> None:
    print(piece, end="", flush=True)


def main() -> None:
    blocks = retrieve(DOC_PATH)

    history: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

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
        try:
            picked = pick_blocks(q, blocks=blocks)
            context = "\n\n".join(b["body"] for b in picked)
            history.append(
                {
                    "role": "user",
                    "content": f"【文档】\n{context}\n\n【问题】\n{q}",
                }
            )
            print("助教 > ", end="", flush=True)
            answer = chat(history, on_delta=show)
            history.append({"role": "assistant", "content": answer})

        except LLMError as e:
            print(f"\n[出错] {e}\n")
            history.pop()  # ← 关键：撤掉那条没被回答的 user 消息
            continue


if __name__ == "__main__":
    main()
