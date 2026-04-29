from fastapi import APIRouter
from typing import List
from models.schemas import MiningSourceResponse, MiningDiscoverRequest, MiningDiscoverResponse, TaskStatusResponse
from services.mining_service import discover_process, discover_petri_net

router = APIRouter(prefix="/mining", tags=["mining"])

@router.post("/petri")
async def discover_petri(req: MiningDiscoverRequest):
    res = discover_petri_net(req.source)
    if "error" in res:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail=res["message"])
    return res

@router.get("/sources", response_model=List[MiningSourceResponse])
async def get_sources():
    return [
        {"id": "O2C", "name": "Order to Cash", "description": "Sales to Payment", "icon": "shopping-cart"},
        {"id": "P2P", "name": "Procure to Pay", "description": "Purchase to Payment", "icon": "truck"},
        {"id": "P2D", "name": "Production to Delivery", "description": "From Production Order to Goods Issue", "icon": "factory"}
    ]

@router.post("/discover", response_model=MiningDiscoverResponse)
async def discover(req: MiningDiscoverRequest):
    import asyncio
    from fastapi import HTTPException
    res = await asyncio.to_thread(discover_process, req.source, req.start_date, req.end_date)
    if "error" in res:
        raise HTTPException(
            status_code=422, 
            detail=res.get("message", "Process discovery failed")
        )
    return res

@router.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    return {"status": "complete", "result": None, "error": None}
