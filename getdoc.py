MAX_DOC_CHARS = 6000


def retrieve(doc_path: str) -> list[dict]:
    text = open(doc_path, encoding="utf-8").read()
    return split_blocks(text)


def get_context(doc_path: str, question: str, mode: str):
    if mode == "chunk":
        blocks = retrieve(doc_path)
        picked = pick_blocks(question, blocks=blocks)
        context = "\n\n".join(b["body"] for b in picked)
        return context
    else:
        text = open(doc_path, encoding="utf-8").read()
        return text[:MAX_DOC_CHARS]


def split_blocks(text: str) -> list[dict]:
    blocks = []
    title = "(开头)"
    lines = []
    for line in text.splitlines():
        if line.startswith("## "):
            if lines:
                blocks.append({"title": title, "body": "\n".join(lines)})
            title = line[3:].split("{#")[0].strip()
            lines = [line]
        else:
            lines.append(line)
    if lines:
        blocks.append({"title": title, "body": "\n".join(lines)})
    return blocks


def pick_blocks(question: str, blocks: list[dict], k: int = 3) -> list[dict]:
    q = bigrams(question)
    scored = []
    for block in blocks:
        score = len(q & bigrams(block["title"] + block["body"]))
        scored.append((score, block))  # 元组：(分数, 完整块)

    scored.sort(key=lambda x: x[0], reverse=True)
    return [block for _, block in scored[:k]]


def bigrams(s: str) -> set[str]:
    s = "".join(ch for ch in s if not ch.isspace())
    return {s[i : i + 2] for i in range(len(s) - 1)}


# def pick_blocks(question: str,blocks: list[dict],k: int = 3) -> list[dict]:
# blocks = split_blocks("docs-vue/src/api/reactivity-core.md")
# for b in blocks[:3]:
#     print(repr(b["title"]), len(b["body"]))
# picked = pick_blocks(
#     "watch 创建的侦听器如何暂停和恢复", retrieve("docs-vue/src/api/reactivity-core.md")
# )
# for b in picked:
#     print("选中:", b["title"])
