import os
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from config import settings
from database import get_session, VBAK
from seed import seed_data
from routers import query, kpi, mining, dashboard, streaming, contracts

# Explicit lifespan handling could be used, but keeping simple startup per spec
app = FastAPI(title="PrimeConSemLayer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Ensure data directory exists
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)

    # Seed database if empty
    try:
        with get_session() as session:
            row = session.execute(select(VBAK).limit(1)).scalar_one_or_none()
            if row is None:
                print("[Startup] Seeding database...")
                seed_data()
                print("[Startup] Database seeded successfully.")
            else:
                print("[Startup] Database already seeded, skipping.")
    except Exception as e:
        print(f"[Startup] DB seed error (non-fatal): {e}")

    # Initialize embedding service — non-fatal if ChromaDB is down
    try:
        from services.embedding_service import embedding_service  # noqa: F401
        print("[Startup] Embedding service ready.")
    except Exception as e:
        print(f"[Startup] Embedding service unavailable (non-fatal): {e}")

    print("[Startup] PrimeConSemLayer API ready")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    print(f"{request.method} {request.url.path} - {duration:.4f}s")
    return response

@app.get("/health")
async def health():
    chroma_ready = False
    try:
        from services.embedding_service import embedding_service
        chroma_ready = embedding_service.collection is not None
    except Exception:
        chroma_ready = False
    return {
        "status": "ok",
        "mock_mode": settings.MOCK_MODE,
        "db_exists": True,
        "chroma_ready": chroma_ready
    }


@app.get("/health/llm")
async def llm_health():
    from services.nl_engine import _get_llm

    status = {
        "status": "ok",
        "mock_mode": settings.MOCK_MODE,
        "model": "gemini-2.0-flash",
        "llm_ready": False,
        "quota_ok": None,
        "error": None,
    }
    try:
        llm = _get_llm()
        status["llm_ready"] = llm is not None
        resp = await llm.ainvoke("Reply only with OK")
        status["quota_ok"] = "ok" in str(getattr(resp, "content", "")).lower()
    except Exception as e:
        status["error"] = str(e)
        msg = str(e).lower()
        if "resourceexhausted" in msg or "quota exceeded" in msg or "429" in msg:
            status["quota_ok"] = False
    return status

app.include_router(query.router, prefix="/api")
app.include_router(kpi.router, prefix="/api", tags=["kpi"])
app.include_router(mining.router, prefix="/api", tags=["mining"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(streaming.router, prefix="/api")
app.include_router(contracts.router)
