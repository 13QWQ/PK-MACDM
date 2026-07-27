"""
向量库接口适配层
队友接口格式（ChromaDB + Ollama） -> 我的格式
"""

import os

import ollama
import chromadb

# ─── 岗位 → (ChromaDB目录, 集合名) 映射 ──────────────────
# 队友每建好一个新岗位的向量库后，把目录和集合名加一行即可
_BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))

JOB_COLLECTION_MAP: dict[str, tuple[str, str]] = {
    "产品经理":      ("my_vector_db", "product_kb"),
    "前端开发工程师": ("db_frontend",  "frontend_kb"),
    "后端开发工程师": ("db_backend",   "backend_kb"),
    "运维工程师":    ("db_ops",       "ops_kb"),
}

# 按 DB 目录缓存 ChromaDB 客户端（同目录复用）
_clients: dict[str, chromadb.PersistentClient] = {}


def _get_client(db_dir: str) -> chromadb.PersistentClient:
    """获取或创建 ChromaDB 客户端（按目录缓存）"""
    if db_dir not in _clients:
        _clients[db_dir] = chromadb.PersistentClient(
            path=os.path.join(_BACKEND_DIR, db_dir)
        )
    return _clients[db_dir]


def _get_collection(job: str):
    """根据岗位名获取对应的 ChromaDB 集合"""
    entry = JOB_COLLECTION_MAP.get(job)
    if not entry:
        return None
    db_dir, collection_name = entry
    return _get_client(db_dir).get_collection(collection_name)


def search_similar_resources(query: str, job: str = "产品经理", top_k: int = 5) -> list:
    """
    相似资源检索（向量检索）

    输入：
        query: 查询文本
        job: 目标岗位（用于选择对应的向量集合）
        top_k: 返回数量

    输出：
        [
            {
                "title": "xxx.txt",
                "content": "文档内容...",
                "score": 0.95
            }
        ]

    如果岗位未配置向量库或检索失败，返回空列表。
    """
    collection = _get_collection(job)
    if not collection:
        return []

    try:
        query_emb = ollama.embeddings(model="nomic-embed-text", prompt=query)["embedding"]
        res = collection.query(query_embeddings=[query_emb], n_results=top_k)

        result_list = []
        for i in range(min(top_k, len(res["ids"][0]))):
            item = {
                "title": res["metadatas"][0][i]["filename"],
                "content": res["documents"][0][i],
                "score": round(1 - res["distances"][0][i], 2),
            }
            result_list.append(item)
        return result_list
    except Exception:
        # Ollama 未启动或其他异常 → 降级返回空列表
        return []


def search_similar_cases(user_vector: list, top_k: int = 5) -> list:
    """
    相似案例检索（暂未接入，保留接口占位）

    输入：
        user_vector: 用户能力向量
        top_k: 返回数量

    输出：
        [
            {
                "case_id": "case_001",
                "similarity": 0.92,
                "user_profile": {"target_job": "前端开发", "study_months": 6},
                "learning_outcome": "成功入职"
            }
        ]
    """
    # 案例检索目前用不上，留空
    return []
