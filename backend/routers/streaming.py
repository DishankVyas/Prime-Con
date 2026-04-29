import asyncio
import json
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from models.schemas import QueryRequest
from services.nl_engine import execute_nl_query

router = APIRouter(prefix="/query", tags=["streaming"])


@router.post("/stream")
async def query_stream(req: QueryRequest):
    async def event_generator():
        try:
            yield {
                "event": "progress",
                "data": json.dumps({"stage": "parsing", "message": "Parsing your question..."}),
            }
            await asyncio.sleep(0.05)

            yield {
                "event": "progress",
                "data": json.dumps({"stage": "schema_retrieval", "message": "Retrieving schema context..."}),
            }
            await asyncio.sleep(0.05)

            yield {
                "event": "progress",
                "data": json.dumps({"stage": "sql_generation", "message": "Generating SQL..."}),
            }

            result = await asyncio.wait_for(execute_nl_query(req.question), timeout=20)

            if "error" in result:
                yield {"event": "error", "data": json.dumps({"error": result["error"]})}
                return

            yield {
                "event": "progress",
                "data": json.dumps({
                    "stage": "executing",
                    "message": f"Query returned {result.get('row_count', 0)} rows",
                }),
            }
            await asyncio.sleep(0.05)

            yield {
                "event": "progress",
                "data": json.dumps({"stage": "summarizing", "message": "Generating AI summary..."}),
            }
            await asyncio.sleep(0.05)

            yield {"event": "result", "data": json.dumps(result, default=str)}
            yield {"event": "complete", "data": json.dumps({"stage": "complete"})}

        except asyncio.TimeoutError:
            yield {"event": "error", "data": json.dumps({"error": "Backend query timed out. Please try a shorter question."})}
        except Exception as e:
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return EventSourceResponse(event_generator())
