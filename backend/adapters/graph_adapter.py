"""
知识图谱接口适配层
队友接口格式 -> 我的格式
"""

from adapters.mock_data import MOCK_KNOWLEDGE_RELATIONS, MOCK_JOB_SKILLS


def get_knowledge_relations(concept: str) -> dict:
    """
    查询知识点关系

    输入：知识点名称
    输出：
        {
            "concept": "贪心算法",
            "prerequisites": ["基础算法", "排序算法"],
            "next_concepts": ["动态规划", "图算法"],
            "related_skills": ["问题分解", "最优子结构"]
        }
    """
    # TODO: 队友接口就绪后，替换为真实调用
    return MOCK_KNOWLEDGE_RELATIONS


def get_job_skill_graph(job_title: str) -> dict:
    """
    查询职业能力图谱

    输入：职业名称
    输出：
        {
            "job": "前端开发工程师",
            "core_skills": ["HTML", "CSS", "JavaScript", "React", "Vue"],
            "skill_dependencies": [{"from": "HTML", "to": "CSS"}, ...]
        }
    """
    # TODO: 队友接口就绪后，替换为真实调用
    return MOCK_JOB_SKILLS
