import asyncio
from langchain_core.prompts import ChatPromptTemplate
from services.nl_engine import _get_llm
from config import settings


def _is_quota_error(err: Exception) -> bool:
    msg = str(err).lower()
    return (
        "resourceexhausted" in msg
        or "quota exceeded" in msg
        or "429" in msg
        or "rate limit" in msg
    )


async def generate_rca(kpi_id: str, kpi_name: str, kpi_value: float, kpi_target: float) -> dict:
    deviation = kpi_value - kpi_target
    direction = "above" if deviation > 0 else "below"

    # In MOCK_MODE return instantly to avoid LLM latency/hangs
    if settings.MOCK_MODE:
        return {
            "summary": f"{kpi_name} is {abs(deviation):.1f} {direction} target.",
            "root_causes": [
                {"rank": 1, "cause": "Transaction delay in upstream process", "impact": "high", "evidence": "Observed KPI variance against threshold."},
                {"rank": 2, "cause": "Manual review/approval bottlenecks", "impact": "medium", "evidence": "Cycle-time heavy process step likely impacted."},
                {"rank": 3, "cause": "Master-data inconsistency", "impact": "low", "evidence": "Potential posting or mapping quality issue."},
            ],
            "recommendations": [
                {"action": "Prioritize high-severity drivers in weekly ops review", "owner": "Process Owner", "timeline": "This week", "expected_impact": "Faster corrective action"},
                {"action": "Add data-quality checks for key posting fields", "owner": "Data Steward", "timeline": "2 weeks", "expected_impact": "Reduced recurring variance"},
            ],
            "trend": "stable"
        }

    prompt = ChatPromptTemplate.from_template("""
You are a SAP ERP process expert performing root cause analysis.

KPI: {kpi_name}
Current Value: {kpi_value}
Target: {kpi_target}
Status: {deviation:.1f} {direction} target

Provide a structured root cause analysis in JSON with this exact structure:
{{
  "summary": "one sentence executive summary",
  "root_causes": [
    {{"rank": 1, "cause": "...", "impact": "high|medium|low", "evidence": "..."}},
    {{"rank": 2, "cause": "...", "impact": "high|medium|low", "evidence": "..."}},
    {{"rank": 3, "cause": "...", "impact": "high|medium|low", "evidence": "..."}}
  ],
  "recommendations": [
    {{"action": "...", "owner": "...", "timeline": "...", "expected_impact": "..."}},
    {{"action": "...", "owner": "...", "timeline": "...", "expected_impact": "..."}}
  ],
  "trend": "improving|deteriorating|stable"
}}

Return raw JSON only, no markdown.
""")

    try:
        llm = _get_llm()
        chain = prompt | llm
        response = await asyncio.wait_for(
            chain.ainvoke({
                "kpi_name": kpi_name,
                "kpi_value": kpi_value,
                "kpi_target": kpi_target,
                "deviation": abs(deviation),
                "direction": direction,
            }),
            timeout=12
        )

        import json
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        return json.loads(content)
    except Exception as e:
        if _is_quota_error(e):
            summary = f"{kpi_name} is {abs(deviation):.1f} {direction} target. Gemini quota exceeded; using deterministic RCA."
        else:
            summary = f"{kpi_name} is {abs(deviation):.1f} {direction} target."
        return {
            "summary": summary,
            "root_causes": [
                {"rank": 1, "cause": "Transaction delay in upstream process", "impact": "high", "evidence": "Observed KPI variance against threshold."},
                {"rank": 2, "cause": "Manual review/approval bottlenecks", "impact": "medium", "evidence": "Cycle-time heavy process step likely impacted."},
                {"rank": 3, "cause": "Master-data inconsistency", "impact": "low", "evidence": "Potential posting or mapping quality issue."},
            ],
            "recommendations": [{"action": "Review data manually", "owner": "Analyst", "timeline": "Immediate", "expected_impact": "Clarity"}],
            "trend": "stable"
        }
