import os

from vector_search import search_similar_docs
from chat_history import ChatHistory
from db_manager import load_config


PROMPT_TEMPLATE = """你是一个专业的课程销售顾问。请根据以下知识库内容和对话历史，回答用户的问题。

知识库内容：
{context}

对话历史：
{history}

用户问题：{question}

请提供专业、友好的回答。如果知识库中没有相关信息，请如实告知并建议用户联系客服。"""


def get_llm_response(query: str, chat_history: ChatHistory) -> str:
    config = load_config()

    relevant_docs = search_similar_docs(query)
    context = "\n".join([doc["content"] for doc in relevant_docs])

    history_text = chat_history.get_formatted_history()

    prompt = PROMPT_TEMPLATE.format(
        context=context,
        history=history_text if history_text else "无",
        question=query,
    )

    try:
        import dashscope
        from dashscope import Generation

        dashscope.api_key = os.environ.get("DASHSCOPE_API_KEY")

        response = Generation.call(
            model=config["chat_model_name"],
            prompt=prompt,
            result_format="message",
        )

        if response.status_code == 200:
            return response.output.choices[0].message.content
        else:
            return f"抱歉，处理请求时出现错误：{response.message}"
    except Exception as e:
        return f"抱歉，调用模型时出现错误：{str(e)}"


if __name__ == "__main__":
    history = ChatHistory()
    history.add_message("user", "你好")
    history.add_message("assistant", "你好！我是课程销售顾问，有什么可以帮您的吗？")

    response = get_llm_response("你们有什么课程？", history)
    print(response)
