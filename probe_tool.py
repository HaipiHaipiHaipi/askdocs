import json

from getdoc import pick_blocks, retrieve
from llm import MODEL, SEARCH_TOOL, TEMPERATURE, THINKING, client
from main import DOC_PATH

doc_path = "docs/sample.md"

BLOCKS = retrieve(DOC_PATH)
BLOCKS1 = retrieve(doc_path=doc_path)


def search_docs(query: str) -> str:
    picked = pick_blocks(query, BLOCKS1, k=2)
    return "\n\n".join(b["body"] for b in picked)


messages = [
    {
        "role": "system",
        "content": "你可以调用 search_docs 查文档。查到内容后必须回答。",
    },
]

while True:  # 外层：对话
    q = input("\n你 > ").strip()
    if not q:
        continue
    if q in ("/exit", "exit"):
        break

    messages.append({"role": "user", "content": q})

    for round_no in range(1, 6):  # 内层：工具轮次
        r = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=[SEARCH_TOOL],
            temperature=TEMPERATURE,
            extra_body={"thinking": {"type": THINKING}},
        )
        msg = r.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:  # 它给答案了
            print(f"\n助教 > {msg.content}\n")
            break  # ← 只跳出内层，回到等下一个问题

        for call in msg.tool_calls:  # 它要工具
            args = json.loads(call.function.arguments)
            print(f"   [检索] {args['query']}")
            result = search_docs(args["query"])
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                }
            )
    else:
        print("\n（超过 5 轮仍未给出答案，已停止）")
