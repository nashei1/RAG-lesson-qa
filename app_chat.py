import streamlit as st
from chat_history import ChatHistory
from rag_service import get_llm_response

st.set_page_config(page_title="智能销售——课程", page_icon="💬")
st.title("💬 智能销售——课程")
st.markdown("---")

# 初始化会话状态
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ChatHistory()

if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入
if prompt := st.chat_input("请输入您的问题..."):
    # 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 获取AI回答
    with st.chat_message("assistant"):
        with st.spinner("正在思考..."):
            response = get_llm_response(prompt, st.session_state.chat_history)
            st.markdown(response)

    # 更新历史记录
    st.session_state.chat_history.add_message("user", prompt)
    st.session_state.chat_history.add_message("assistant", response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# 侧边栏
with st.sidebar:
    st.subheader("操作")
    if st.button("清空对话历史"):
        st.session_state.chat_history.clear()
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.subheader("关于")
    st.markdown("""
    这是一个智能课程销售助手，可以：
    - 回答课程相关问题
    - 提供选课建议
    - 解答常见问题
    - 介绍课程安排和价格
    """)
