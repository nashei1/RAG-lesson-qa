import chromadb
from db_manager import load_config, DashScopeEmbedding


def search_similar_docs(query: str, n_results: int = None) -> list:
    config = load_config()

    if n_results is None:
        n_results = config["similarity_threshold"]

    client = chromadb.PersistentClient(path=config["persist_directory"])
    embedding_fn = DashScopeEmbedding(model_name=config["embedding_model_name"])
    collection = client.get_or_create_collection(
        name=config["collection_name"],
        embedding_function=embedding_fn,
    )

    results = collection.query(query_texts=[query], n_results=n_results)

    docs = []
    if results and results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}
            distance = results["distances"][0][i] if results["distances"] else None
            docs.append({
                "content": doc,
                "source": metadata.get("source", "未知"),
                "distance": distance,
            })
    return docs


if __name__ == "__main__":
    query = "课程价格是多少"
    results = search_similar_docs(query)
    for r in results:
        print(f"来源: {r['source']}")
        print(f"内容: {r['content'][:100]}...")
        print(f"距离: {r['distance']}")
        print("---")
