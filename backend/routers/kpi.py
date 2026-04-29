from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import KpiData, KpiModulesResponse, RcaResponse
from services.kpi_service import get_all_kpis, get_kpi_by_id
from services.rca_service import generate_rca

router = APIRouter(prefix="/kpi", tags=["kpi"])


@router.get("/all", response_model=List[KpiData])
async def get_all():
    return get_all_kpis()


@router.get("/modules", response_model=KpiModulesResponse)
async def get_modules():
    kpis = get_all_kpis()
    return {
        "FI": [k for k in kpis if k["module"] == "FI"],
        "SD": [k for k in kpis if k["module"] == "SD"],
        "MM": [k for k in kpis if k["module"] == "MM"],
        "PP": [k for k in kpis if k["module"] == "PP"],
    }


def _normalize_rca_payload(kpi_id: str, raw: dict) -> dict:
    causes = []
    timeline = []

    if isinstance(raw, dict):
        raw_causes = raw.get("root_causes") or raw.get("causes") or []
        for item in raw_causes:
            causes.append({
                "title": item.get("cause", "Unknown cause"),
                "description": item.get("evidence", "No evidence provided."),
                "severity": item.get("impact", "medium"),
                "affected_records": int(item.get("affected_records", 0) or 0),
                "recommendation": item.get("recommendation", "Review process controls."),
            })

        raw_recommendations = raw.get("recommendations") or []
        for i, rec in enumerate(raw_recommendations[:5]):
            timeline.append({
                "date": f"Step {i + 1}",
                "event": rec.get("action", "Recommended action"),
                "impact": rec.get("expected_impact", "Expected improvement"),
            })

    if not causes:
        causes = [{
            "title": "Variance from target detected",
            "description": "KPI deviated from configured threshold based on current data.",
            "severity": "medium",
            "affected_records": 0,
            "recommendation": "Inspect recent transactions and validate master data quality.",
        }]

    if not timeline:
        timeline = [
            {"date": "T0", "event": "Anomaly detected", "impact": "KPI moved beyond expected range."},
            {"date": "T1", "event": "Investigation initiated", "impact": "Potential process bottlenecks flagged."},
            {"date": "T2", "event": "Root cause identified", "impact": "Primary driver isolated."},
        ]

    summary = (
        raw.get("summary")
        if isinstance(raw, dict) and raw.get("summary")
        else "KPI anomaly detected. Review likely process and data quality drivers."
    )

    return {"kpi_id": kpi_id, "rca": {"summary": summary, "causes": causes, "timeline": timeline}}


# GET /rca/{kpi_id} MUST be registered before GET /{kpi_id}
@router.get("/rca/{kpi_id}", response_model=RcaResponse)
async def get_rca(kpi_id: str):
    kpis = get_all_kpis()
    kpi = next((k for k in kpis if k["id"] == kpi_id), None)
    if not kpi:
        raise HTTPException(status_code=404, detail=f"KPI {kpi_id} not found")
    raw = await generate_rca(kpi_id, kpi["name"], kpi["value"], kpi.get("threshold_amber", 0.0))
    return _normalize_rca_payload(kpi_id, raw)


@router.post("/{kpi_id}/rca", response_model=RcaResponse)
async def post_rca(kpi_id: str):
    return await get_rca(kpi_id)


# Wildcard route LAST
@router.get("/{kpi_id}", response_model=KpiData)
async def get_kpi(kpi_id: str):
    kpi = get_kpi_by_id(kpi_id)
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI not found")
    return kpi
