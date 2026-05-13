from typing import List, Dict


class ChatHistory:
    def __init__(self, max_history: int = 10):
        self.history: List[Dict[str, str]] = []
        self.max_history = max_history

    def add_message(self, role: str, content: str):
        """添加消息到历史记录"""
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-(self.max_history * 2):]

    def get_history(self) -> List[Dict[str, str]]:
        """获取历史记录"""
        return self.history

    def get_formatted_history(self) -> str:
        """获取格式化的历史记录字符串"""
        if not self.history:
            return ""

        formatted = []
        for msg in self.history:
            role = "用户" if msg["role"] == "user" else "助手"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)

    def clear(self):
        """清空历史记录"""
        self.history = []

    def get_last_n_pairs(self, n: int = 3) -> List[Dict[str, str]]:
        """获取最近n轮对话"""
        return self.history[-(n * 2):] if len(self.history) >= n * 2 else self.history
