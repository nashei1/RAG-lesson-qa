# 智能销售——课程

基于 Streamlit + ChromaDB + 阿里云百炼平台的智能课程销售系统。

## 功能概述

### 系统一：知识库管理
- 上传 TXT 格式的知识库文件
- 自动 MD5 去重，避免重复入库
- 文本分块后存入 ChromaDB 向量数据库

### 系统二：智能对话
- 基于 RAG 的问答系统
- 向量检索匹配知识库内容
- 支持多轮对话，自动维护历史记录

## 项目结构

```
├── config                # 配置文件
├── data/                 # 知识库文件目录
├── requirements.txt      # Python 依赖
├── db_manager.py         # 数据库管理（入库、去重、分块）
├── app_kb.py             # 知识库上传网页
├── vector_search.py      # 向量检索模块
├── chat_history.py       # 对话历史管理
├── rag_service.py        # RAG 服务（提示词组装 + LLM 调用）
└── app_chat.py           # 智能对话网页
```

## 快速开始

### 1. 创建环境

```bash
conda create -n lesson python=3.10
conda activate lesson
pip install -r requirements.txt
```

### 2. 配置环境变量

设置阿里云百炼平台的 API Key：

```bash
export DASHSCOPE_API_KEY="your-api-key"
```

### 3. 初始化数据库

```bash
python db_manager.py
```

首次运行会处理 `data/` 目录下的所有 TXT 文件，生成 `md5.text` 和 `chroma_db/` 目录。

### 4. 启动应用

```bash
# 知识库管理（端口 8501）
streamlit run app_kb.py

# 智能对话（端口 8502）
streamlit run app_chat.py
```

## 配置说明

`config` 文件中的主要参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `md5_path` | MD5 记录文件路径 | `./md5.text` |
| `collection_name` | ChromaDB 集合名 | `rag` |
| `persist_directory` | ChromaDB 存储目录 | `./chroma_db` |
| `chunk_size` | 文本分块大小 | `1000` |
| `chunk_overlap` | 分块重叠长度 | `100` |
| `similarity_threshold` | 检索返回文档数 | `1` |
| `embedding_model_name` | 向量模型 | `text-embedding-v4` |
| `chat_model_name` | 对话模型 | `qwen3-max` |

## 技术栈

- **前端**：Streamlit
- **向量数据库**：ChromaDB
- **Embedding**：阿里云 DashScope text-embedding-v4
- **LLM**：阿里云百炼 qwen3-max
- **文本分割**：LangChain Text Splitters
