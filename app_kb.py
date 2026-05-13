import streamlit as st
from db_manager import load_config, process_uploaded_file, load_md5_records

st.set_page_config(page_title="知识库管理", page_icon="📚")
st.title("📚 知识库管理")
st.markdown("---")

# 加载配置
config = load_config()

# 文件上传区域
st.subheader("上传知识库文件")
uploaded_file = st.file_uploader("选择TXT文件", type=["txt"], help="支持TXT格式的文本文件")

if uploaded_file is not None:
    file_content = uploaded_file.read().decode("utf-8")
    st.text_area("文件预览", file_content[:500] + "..." if len(file_content) > 500 else file_content, height=150)

    if st.button("上传并处理"):
        with st.spinner("正在处理文件..."):
            result = process_uploaded_file(uploaded_file.name, file_content, config)

            if result["status"] == "success":
                st.success(f"✅ 文件上传成功！已分割为 {result['chunks']} 个文本块")
            elif result["status"] == "skipped":
                st.warning(f"⚠️ 文件已存在，跳过处理")
            else:
                st.error(f"❌ 处理失败")

st.markdown("---")

# 显示已有知识库统计
st.subheader("知识库统计")
md5_set = load_md5_records(config["md5_path"])
st.metric("已处理文件数", len(md5_set))

# 显示提示
st.markdown("---")
st.subheader("使用说明")
st.markdown("""
1. 上传TXT格式的知识库文件
2. 系统会自动计算MD5进行去重
3. 文件内容会被分割成小块存入向量数据库
4. 重复文件会自动跳过
""")
