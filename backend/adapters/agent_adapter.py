"""Drop-in adapter for PK-MACDM backend/adapters/agent_adapter.py.

The three public functions intentionally match the reference repository's
existing calls.  Do not change them to accept separate score, weekly-hours,
materials, or dialogue fields.
"""

from __future__ import annotations

from .agent_runtime import AgentRuntime


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


def review_resources(package_id: str, resources: list[dict]) -> list[dict]:
    """层2：逐条资源做知识库校验（防幻觉），返回每条的校验结论。

    verdict → status 映射：grounded→passed / partial→partial / ungrounded→blocked / 无来源→skipped
    """
    from .guardrail import check_hallucination

    verdict_to_status = {"grounded": "passed", "partial": "partial", "ungrounded": "blocked"}
    results = []
    for r in resources:
        source_text = r.get("source_text", "")
        if not source_text:
            results.append({
                "resource_id": r.get("resource_id", ""),
                "status": "skipped",
                "reason": "无知识库来源，跳过校验",
            })
            continue
        guard = check_hallucination(source_text, r.get("body", ""))
        results.append({
            "resource_id": r.get("resource_id", ""),
            "status": verdict_to_status.get(guard.get("verdict", "grounded"), "passed"),
            "reason": guard.get("reason", ""),
        })
    return results


def get_last_trace() -> dict:
    """Optional hook for the future Agent dashboard; current backend ignores it."""
    return dict(_runtime.last_trace)
