"""
AI诊断接口适配层
队友接口格式 -> 我的格式
"""

from adapters.mock_data import MOCK_DIAGNOSIS, MOCK_RESOURCE, MOCK_RESOURCE_BY_TYPE, MOCK_PATH
from dimensions import label_vector


def diagnose(user_id: str, target_job: str, user_input: str) -> dict:
    """
    调用队友的能力诊断接口

    输入：
        user_id: 用户ID
        target_job: 目标职业
        user_input: 用户自由文本输入（技能、项目、经验等）

    输出（统一格式）：
        {
            "overall_mastery": 0.72,
            "ability_vector": [
                {"index":1, "name":"编程基础", "value":0.8, "weight":"high", "category":"通用基础"},
                ...
            ],
            "knowledge_gaps": ["贪心算法", ...],
            "confidence": 0.85
        }
    """
    # TODO: 队友接口就绪后，替换为真实调用
    # from config import settings
    # import requests
    # response = requests.post(f"{settings.AGENT_API_URL}/diagnose", json={
    #     "uid": user_id,
    #     "job": target_job,
    #     "user_input": user_input
    # })
    # raw = response.json()
    # return {
    #     "overall_mastery": raw["mastery_score"],
    #     "ability_vector": label_vector(raw["vector"], target_job),
    #     "knowledge_gaps": raw["weaknesses"],
    #     "confidence": raw.get("confidence", 0.85)
    # }

    # 暂时返回Mock数据，并通过label_vector附加维度名称和岗位权重
    raw = MOCK_DIAGNOSIS
    return {
        "overall_mastery": raw["overall_mastery"],
        "ability_vector": label_vector(raw["ability_vector"], target_job),
        "knowledge_gaps": raw["knowledge_gaps"],
        "confidence": raw["confidence"],
    }


def generate_resource(knowledge_point: str, user_level: float, resource_type: str) -> dict:
    """
    调用队友的学习资源生成接口

    输入：
        knowledge_point: 知识点
        user_level: 用户水平 (0-1)
        resource_type: 资源类型 (讲义/练习/案例/视频脚本)

    输出（统一格式）：
        {
            "content_type": "讲义",
            "title": "贪心算法入门指南",
            "body": "...",
            "difficulty": 3
        }
    """
    # TODO: 队友接口就绪后，替换为真实调用
    base = MOCK_RESOURCE_BY_TYPE.get(resource_type, MOCK_RESOURCE)
    return {
        "content_type": resource_type,
        "title": base["title"].replace("贪心算法", knowledge_point),
        "body": base["body"].replace("贪心算法", knowledge_point),
        "difficulty": base["difficulty"],
    }


def plan_learning_path(user_id: str, target_job: str, current_ability: list) -> list:
    """
    调用队友的学习路径规划接口

    输入：
        user_id: 用户ID
        target_job: 目标职业
        current_ability: 当前能力向量 [0.8, 0.6, ...]

    输出（统一格式）：
        [
            {"step": 1, "knowledge_point": "贪心算法", "resource_type": "讲义", "estimated_time": 30, "prerequisite": "基础算法"},
            ...
        ]
    """
    # TODO: 队友接口就绪后，替换为真实调用
    return MOCK_PATH
