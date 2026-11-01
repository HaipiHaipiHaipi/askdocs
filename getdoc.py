MAX_DOC_CHARS = 6000

def retrieve(doc_path: str) -> str:
    text = open(doc_path,encoding="utf-8").read()
    if len(text) <= MAX_DOC_CHARS:
        return text
    return text[:MAX_DOC_CHARS]+"\n\n(原文过长，仅加载部分)"
