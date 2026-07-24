"""
向量库接口适配层
队友接口格式 -> 我的格式
"""

from adapters.mock_data import MOCK_SIMILAR_CASES


def search_similar_cases(user_vector: list, top_k: int = 5) -> list:
    """
    相似案例检索

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
    # TODO: 队友接口就绪后，替换为真实调用
    return MOCK_SIMILAR_CASES


def search_similar_resources(query: str, top_k: int = 5) -> list:
    """
    相似资源检索

    输入：
        query: 查询内容
        top_k: 返回数量

    输出：
        [
            {
                "resource_id": "res_001",
                "title": "贪心算法详解",
                "content": "...",
                "similarity": 0.95
            }
        ]
    """
    # TODO: 队友接口就绪后，替换为真实调用
    # 降级方案：用MySQL模糊查询替代
    return []
