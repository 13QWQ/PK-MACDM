"""
向量库接口适配层
队友接口格式（Qdrant + BGE-M3） -> 我的格式

依赖 qdrant-client、FlagEmbedding，仅在调用检索函数时按需导入，
未安装时后端其余功能不受影响，搜索接口返回空列表。
"""

import os

# ─── 岗位 → Qdrant career_id 映射 ──────────────────
# 队友用英文 career_id 标识岗位，这里做中文名到英文的映射

JOB_CAREER_MAP: dict[str, str] = {
    "产品经理":      "product_manager",
    "前端开发工程师": "frontend_engineer",
    "后端开发工程师": "java_backend_engineer",
    "运维工程师":    "operations_engineer",
}

_BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
_QDRANT_PATH = os.path.join(_BACKEND_DIR, "qdrant_storage")
_MODEL_PATH = os.path.join(_BACKEND_DIR, "bge-m3")

_client = None
_model = None
_imports_checked: bool = False


def _ensure_imports() -> bool:
    """按需导入 qdrant-client / FlagEmbedding，未安装返回 False"""
    global _imports_checked, QdrantClient, Filter, FieldCondition, MatchValue, BGEM3FlagModel
    if _imports_checked:
        return True
    try:
        from qdrant_client import QdrantClient as _QdrantClient
        from qdrant_client.models import Filter as _Filter, FieldCondition as _FieldCondition, MatchValue as _MatchValue
        from FlagEmbedding import BGEM3FlagModel as _BGEM3FlagModel

        QdrantClient = _QdrantClient
        Filter = _Filter
        FieldCondition = _FieldCondition
        MatchValue = _MatchValue
        BGEM3FlagModel = _BGEM3FlagModel
        _imports_checked = True
        return True
    except ImportError:
        return False


def _get_client():
    """获取或创建 Qdrant 本地客户端（单例）"""
    global _client
    if _client is None:
        _client = QdrantClient(path=_QDRANT_PATH)
    return _client


def _get_model():
    """获取或创建 BGE-M3 嵌入模型（单例）"""
    global _model
    if _model is None:
        _model = BGEM3FlagModel(_MODEL_PATH, use_fp16=True)
    return _model


def search_similar_resources(query: str, job: str = "产品经理", top_k: int = 5) -> list:
    """
    相似资源检索（向量检索）

    输入：
        query: 查询文本
        job: 目标岗位（用于过滤对应岗位的知识库）
        top_k: 返回数量

    输出：
        [
            {
                "title": "xxx.txt",
                "content": "文档内容...",
                "score": 0.95
            }
        ]

    如果 qdrant-client/FlagEmbedding 未安装、模型未下载、或岗位未配置，返回空列表。
    """
    if not _ensure_imports():
        return []

    career_id = JOB_CAREER_MAP.get(job)
    if not career_id:
        return []

    try:
        model = _get_model()
        client = _get_client()

        query_vec = model.encode([query], return_dense=True)["dense_vecs"][0].tolist()

        response = client.query_points(
            collection_name="career_knowledge_v1",
            query=query_vec,
            query_filter=Filter(must=[
                FieldCondition(key="career_id", match=MatchValue(value=career_id)),
                FieldCondition(key="review_status", match=MatchValue(value="ready_for_reembedding")),
            ]),
            limit=top_k,
        )

        result_list = []
        for hit in response.points:
            payload = hit.payload or {}
            result_list.append({
                "title": payload.get("source_document", ""),
                "content": payload.get("content", ""),
                "score": round(float(hit.score), 2),
                "id": str(hit.id),
            })
        return result_list
    except Exception:
        return []


def search_all_careers(query: str, top_k: int = 3) -> list:
    """
    跨岗位检索（资源表未存岗位，回填旧数据时用）

    与 search_similar_resources 同逻辑，但不按 career_id 过滤，
    仅保留 review_status == "ready_for_reembedding" 的质量过滤。

    返回结构同 search_similar_resources：[{"title","content","score","id"}]
    """
    if not _ensure_imports():
        return []

    try:
        model = _get_model()
        client = _get_client()

        query_vec = model.encode([query], return_dense=True)["dense_vecs"][0].tolist()

        response = client.query_points(
            collection_name="career_knowledge_v1",
            query=query_vec,
            query_filter=Filter(must=[
                FieldCondition(key="review_status", match=MatchValue(value="ready_for_reembedding")),
            ]),
            limit=top_k,
        )

        result_list = []
        for hit in response.points:
            payload = hit.payload or {}
            result_list.append({
                "title": payload.get("source_document", ""),
                "content": payload.get("content", ""),
                "score": round(float(hit.score), 2),
                "id": str(hit.id),
            })
        return result_list
    except Exception:
        return []


def ensure_accessible() -> bool:
    """预检向量库是否可访问（本地模式单进程，后端运行时 Qdrant 会被锁，返回 False）"""
    if not _ensure_imports():
        return False
    try:
        _get_client()
        return True
    except Exception:
        return False


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
    return []
