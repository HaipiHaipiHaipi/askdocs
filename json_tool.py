JSON_OUTPUT_TOOL = {
    "type": "function",
    "function": {
        "name": "save_game",
        "description": "保存一条游戏记录",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "游戏名字"},
                "tags": {"type": "array", "description": "游戏类型"},
                "score": {"type": "number", "description": "游戏评分"},
            },
            "required": ["title", "tags", "score"],
        },
    },
}
