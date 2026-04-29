from fastapi import APIRouter, HTTPException
from models.schemas import DashboardGenerateRequest
from services.dashboard_service import generate_dashboard

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.post("/generate")
async def generate(req: DashboardGenerateRequest):
    result = await generate_dashboard(req.prompt)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result
