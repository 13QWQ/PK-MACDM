"""
防幻觉校验 —— 用 LLM 比对生成内容与知识库原文，判断是否存在编造

不再依赖本地 Ollama，直接用 llm_config.json 配置的 API 完成校验。
"""

from __future__ import annotations

import json

from .llm_client import chat_json

GUARD_SYSTEM = """你是一个严谨的事实核查助手。请判断【AI 回答】是否忠实于【参考文档】。

请对【AI 回答】的忠实度进行三档分级：
- grounded（有依据）：回答的核心内容与参考文档一致，允许合理的归纳、转述、举例或基于文档的推论；扩展补充的属于该主题公认、正确的标准知识，且没有与文档矛盾或编造错误
- partial（部分匹配）：回答大部分基于文档，但有小部分与文档有出入，或扩展补充较多、方向仍与文档一致
- ungrounded（无依据）：回答与参考文档明显矛盾，或编造了与文档冲突的错误事实（概念定义错误、张冠李戴、把 A 说成 B 等）。注意：仅仅"文档没提到、但属于该主题正确公认知识"的合理扩充，不算 ungrounded

必须严格只输出以下 JSON 格式：
{"verdict": "grounded|partial|ungrounded", "reason": "简要说明判断依据"}"""


def check_hallucination(context_text: str, response_text: str) -> dict:
    """用 LLM 校验 response 是否忠实于 context，返回 {"verdict", "has_hallucination", "reason"}"""
    if not context_text or not response_text:
        return {
            "verdict": "needs_manual_review",
            "has_hallucination": True,
            "reason": "缺少参考原文或待审核回答，无法完成防幻觉校验",
        }

    user_msg = f"""【参考文档】
{context_text[:4000]}

【AI 回答】
{response_text[:3000]}"""

    try:
        result = chat_json(GUARD_SYSTEM, user_msg)
        if not result:
            return {
                "verdict": "needs_manual_review",
                "has_hallucination": True,
                "reason": "LLM 校验未返回有效结果，禁止自动放行",
            }
        verdict = str(result.get("verdict", "")).lower().strip()
        if verdict not in ("grounded", "partial", "ungrounded"):
            return {
                "verdict": "needs_manual_review",
                "has_hallucination": True,
                "reason": "LLM 返回的审核 verdict 无法解析，禁止自动放行",
            }
        return {
            "verdict": verdict,
            "has_hallucination": verdict != "grounded",
            "reason": str(result.get("reason", "LLM 校验完成")),
        }
    except Exception as e:
        return {
            "verdict": "needs_manual_review",
            "has_hallucination": True,
            "reason": f"LLM 校验异常 ({e})，已转人工复核",
        }
