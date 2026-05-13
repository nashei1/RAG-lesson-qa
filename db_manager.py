import hashlib
import os
from pathlib import Path
from typing import List

import chromadb
import dashscope
from chromadb import EmbeddingFunction, Documents, Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

dashscope.api_key = os.environ.get("DASHSCOPE_API_KEY", "")


class DashScopeEmbedding(EmbeddingFunction):
    def __init__(self, model_name: str = "text-embedding-v4"):
        self.model_name = model_name

    def __call__(self, input: Documents) -> Embeddings:
        resp = dashscope.TextEmbedding.call(model=self.model_name, input=input)
        if resp.status_code == 200:
            return [item["embedding"] for item in resp.output["embeddings"]]
        raise RuntimeError(f"Embedding API error: {resp.code} - {resp.message}")


def load_config() -> dict:
    config = {}
    with open("config", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "#" in line:
                    line = line[:line.index("#")].strip()
                if "=" in line:
                    key, value = line.split(" = ", 1)
                    key = key.strip()
                    value = value.strip().strip('"')
                    if key in ["chunk_size", "chunk_overlap", "similarity_threshold", "max_split_char_number"]:
                        config[key] = int(value)
                    elif key == "separators":
                        config[key] = eval(value)
                    else:
                        config[key] = value
    return config


def calculate_md5(content: str) -> str:
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def load_md5_records(md5_path: str) -> set:
    md5_set = set()
    if os.path.exists(md5_path):
        with open(md5_path, "r", encoding="utf-8") as f:
            for line in f:
                md5_set.add(line.strip())
    return md5_set


def save_md5_record(md5_path: str, md5_value: str):
    with open(md5_path, "a", encoding="utf-8") as f:
        f.write(md5_value + "\n")


def split_text(text: str, config: dict) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config["chunk_size"],
        chunk_overlap=config["chunk_overlap"],
        separators=config["separators"],
        length_function=len,
    )
    return splitter.split_text(text)


def get_chroma_collection(config: dict):
    client = chromadb.PersistentClient(path=config["persist_directory"])
    embedding_fn = DashScopeEmbedding(model_name=config["embedding_model_name"])
    collection = client.get_or_create_collection(
        name=config["collection_name"],
        embedding_function=embedding_fn,
    )
    return collection


def process_file(file_path: str, config: dict, md5_set: set) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    md5_value = calculate_md5(content)
    if md5_value in md5_set:
        return {"status": "skipped", "file": file_path, "reason": "已存在"}

    chunks = split_text(content, config)
    collection = get_chroma_collection(config)
    file_name = Path(file_path).stem

    for i, chunk in enumerate(chunks):
        doc_id = f"{file_name}_{i}"
        collection.add(
            documents=[chunk],
            ids=[doc_id],
            metadatas=[{"source": file_name, "chunk_index": i}],
        )

    save_md5_record(config["md5_path"], md5_value)
    md5_set.add(md5_value)
    return {"status": "success", "file": file_path, "chunks": len(chunks)}


def process_uploaded_file(file_name: str, file_content: str, config: dict) -> dict:
    md5_set = load_md5_records(config["md5_path"])
    md5_value = calculate_md5(file_content)

    if md5_value in md5_set:
        return {"status": "skipped", "file": file_name, "reason": "已存在"}

    chunks = split_text(file_content, config)
    collection = get_chroma_collection(config)
    file_stem = Path(file_name).stem

    for i, chunk in enumerate(chunks):
        doc_id = f"{file_stem}_{i}"
        collection.add(
            documents=[chunk],
            ids=[doc_id],
            metadatas=[{"source": file_stem, "chunk_index": i}],
        )

    save_md5_record(config["md5_path"], md5_value)
    return {"status": "success", "file": file_name, "chunks": len(chunks)}


def init_database():
    config = load_config()
    md5_set = load_md5_records(config["md5_path"])
    results = []
    data_dir = Path("data")
    if not data_dir.exists():
        return results
    for file_path in data_dir.glob("*.txt"):
        result = process_file(str(file_path), config, md5_set)
        results.append(result)
    return results


if __name__ == "__main__":
    results = init_database()
    for r in results:
        print(r)
