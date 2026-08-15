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
_QDRANT_PATH = os.getenv("QDRANT_PATH", os.path.join(_BACKEND_DIR, "qdrant_storage"))
_QDRANT_URL = os.getenv("QDRANT_URL", "").strip()
_QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "").strip() or None
_QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "career_knowledge_v1")
_MODEL_PATH = os.getenv("EMBEDDING_MODEL_PATH", os.path.join(_BACKEND_DIR, "bge-m3"))

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
    """获取 Qdrant 客户端：配置 URL 时使用服务模式，否则使用本地文件模式。"""
    global _client
    if _client is None:
        if _QDRANT_URL:
            _client = QdrantClient(url=_QDRANT_URL, api_key=_QDRANT_API_KEY)
        else:
            _client = QdrantClient(path=_QDRANT_PATH)
    return _client


def _get_model():
    """获取或创建 BGE-M3 嵌入模型（单例）"""
    global _model
    if _model is None:
        _model = BGEM3FlagModel(_MODEL_PATH, use_fp16=True)
    return _model


def _serialize_hit(hit) -> dict:
    """将 Qdrant 点转换为统一的知识库来源结构。

    `point_id` 是 Qdrant 的内部存储 ID，不能作为业务来源 ID；
    `source_chunk_id` 必须来自知识库 payload，供资源审核和页面追溯。
    """
    payload = hit.payload or {}
    source_chunk_id = str(payload.get("source_chunk_id") or "").strip()
    content = str(payload.get("content") or "")
    try:
        score = round(float(hit.score), 2)
    except (TypeError, ValueError):
        score = 0.0

    candidate_requirement_ids = payload.get("candidate_requirement_ids") or []
    if not isinstance(candidate_requirement_ids, list):
        candidate_requirement_ids = [str(candidate_requirement_ids)]

    return {
        # 兼容旧调用方，但不再把 Qdrant point ID 当作业务 ID。
        "id": source_chunk_id,
        "source_chunk_id": source_chunk_id,
        "parent_source_chunk_id": str(payload.get("parent_source_chunk_id") or ""),
        "point_id": str(hit.id),
        "career_id": str(payload.get("career_id") or ""),
        "candidate_requirement_ids": [str(x) for x in candidate_requirement_ids],
        "review_status": str(payload.get("review_status") or ""),
        "title": str(payload.get("source_document") or ""),
        "content": content,
        "score": score,
    }


def search_similar_resources(query: str, job: str = "产品经理", top_k: int = 5) -> list:
    """
    相似资源检索（向量检索）

    输入：
        query: 查询文本
        job: 目标岗位（用于过滤对应岗位的知识库）
        top_k: 返回数量

    输出：包含 `source_chunk_id`、原文、岗位、审核状态和检索分数的来源对象。

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
            collection_name=_QDRANT_COLLECTION,
            query=query_vec,
            query_filter=Filter(must=[
                FieldCondition(key="career_id", match=MatchValue(value=career_id)),
                FieldCondition(key="review_status", match=MatchValue(value="ready_for_reembedding")),
            ]),
            limit=top_k,
        )

        result_list = [_serialize_hit(hit) for hit in response.points]
        return result_list
    except Exception:
        return []


def search_all_careers(query: str, top_k: int = 3) -> list:
    """
    跨岗位检索（资源表未存岗位，回填旧数据时用）

    与 search_similar_resources 同逻辑，但不按 career_id 过滤，
    仅保留 review_status == "ready_for_reembedding" 的质量过滤。

    返回结构同 search_similar_resources，`source_chunk_id` 仍必须来自 payload。
    """
    if not _ensure_imports():
        return []

    try:
        model = _get_model()
        client = _get_client()

        query_vec = model.encode([query], return_dense=True)["dense_vecs"][0].tolist()

        response = client.query_points(
            collection_name=_QDRANT_COLLECTION,
            query=query_vec,
            query_filter=Filter(must=[
                FieldCondition(key="review_status", match=MatchValue(value="ready_for_reembedding")),
            ]),
            limit=top_k,
        )

        result_list = [_serialize_hit(hit) for hit in response.points]
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
