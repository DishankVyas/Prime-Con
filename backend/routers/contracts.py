from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from services.kpi_service import get_all_kpis
from services.mining_service import discover_process
from services.nl_engine import execute_nl_query
from routers.kpi import get_rca

router = APIRouter(tags=["contracts"])


class ProcessMiningRequest(BaseModel):
    source: str = Field(default="O2C")
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class RootCauseRequest(BaseModel):
    kpi_id: str


@router.post("/nl-query")
async def nl_query(req: dict):
    question = (req or {}).get("question", "").strip()
    if not question:
        raise HTTPException(status_code=422, detail="question is required")
    result = await execute_nl_query(question)
    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])
    return {
        "data": result.get("data", []),
        "chart": result.get("chart_config", {}),
        "sql": result.get("sql", ""),
        "summary": result.get("ai_summary", ""),
    }


@router.post("/process-mining")
async def process_mining(req: ProcessMiningRequest):
    result = discover_process(req.source, req.start_date, req.end_date)
    if "error" in result:
        raise HTTPException(status_code=422, detail=result.get("message", "Process mining failed"))
    return result


@router.get("/kpi")
async def kpi_list():
    return get_all_kpis()


@router.post("/root-cause")
async def root_cause(req: RootCauseRequest):
    rca_payload = await get_rca(req.kpi_id)
    summary = rca_payload["rca"]["summary"]
    primary = rca_payload["rca"]["causes"][0]
    return {
        "issue": summary,
        "cause": primary.get("title", "Unknown cause"),
        "confidence": 0.8,
        "details": rca_payload,
    }
