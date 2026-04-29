from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import QueryRequest, QueryResponse
from services.nl_engine import execute_nl_query

router = APIRouter(prefix="/query", tags=["query"])

@router.get("/suggestions", response_model=List[str])
async def get_suggestions():
    return [
        "Show revenue by customer",
        "Top 5 overdue invoices",
        "Open AP amounts by vendor",
        "Inventory value by plant",
        "Delayed production orders",
        "Sales orders created this week",
        "Purchase orders without goods receipt",
        "Average order to cash cycle time",
        "Scrap rate by material",
        "Highest value purchase orders",
        "Vendor on-time delivery rate",
        "Most frequently returned items"
    ]

@router.post("", response_model=QueryResponse)
async def post_query(req: QueryRequest):
    result = await execute_nl_query(req.question)
    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])
    return result
