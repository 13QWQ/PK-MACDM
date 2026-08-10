"""Drop-in adapter for PK-MACDM backend/adapters/agent_adapter.py.

The three public functions intentionally match the reference repository's
existing calls.  Do not change them to accept separate score, weekly-hours,
materials, or dialogue fields.
"""

from __future__ import annotations

from .agent_runtime import AgentRuntime
from .mock_data import MOCK_REVIEW_RESULT


_runtime = AgentRuntime()


def diagnose(user_id: str, target_job: str, user_input: str) -> dict:
    """Diagnose one free-text user description for any supported role."""
    return _runtime.diagnose(user_id=user_id, target_job=target_job, user_input=user_input)


def generate_resource(knowledge_point: str, user_level: float, resource_type: str, gap_id: str = "") -> dict:
    """Generate one resource using the current request's target-role context."""
    return _runtime.generate_resource(
        knowledge_point=knowledge_point,
        user_level=user_level,
        resource_type=resource_type,
    )


def plan_learning_path(user_id: str, target_job: str, current_ability: list) -> list:
    """Generate a path from the backend's raw 16-dimension vector."""
    return _runtime.plan_learning_path(
        user_id=user_id,
        target_job=target_job,
        current_ability=current_ability,
    )


def review_resources(package_id: str, resources: list[dict]) -> dict:
    """内容审核与纠偏（Mock 版本，待 resources 表添加 source_chunk_id 列后接入正式审核）"""
    return MOCK_REVIEW_RESULT


def get_last_trace() -> dict:
    """Optional hook for the future Agent dashboard; current backend ignores it."""
    return dict(_runtime.last_trace)
