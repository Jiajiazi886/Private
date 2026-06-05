def build_summary_prompt(old_summary: str, new_messages_text: str) -> list[dict]:
    system_prompt = """
你是一个角色扮演聊天应用的长期记忆整理器。
你的任务是把旧摘要和新增聊天记录合并成新的长期摘要。

必须保留：
1. 用户的重要偏好。
2. 角色和用户的关系变化。
3. 已经发生的重要剧情。
4. 角色或用户做出的承诺、约定、未完成事件。
5. 重要地点、人物、组织、世界观设定。
6. 用户明确要求记住的信息。

必须删除：
1. 普通寒暄。
2. 临时情绪。
3. 重复内容。
4. 对后续剧情没有影响的细节。

输出要求：
1. 使用中文。
2. 分条写。
3. 不要超过 1000 字。
4. 不要编造聊天记录里没有的信息。
""".strip()
    return [
        {'role': 'system', 'content': system_prompt},
        {
            'role': 'user',
            'content': f'【旧摘要】\n{old_summary or "暂无"}\n\n【新增聊天记录】\n{new_messages_text}\n\n请输出合并后的新长期摘要。',
        },
    ]
