# PrimeConSemLayer

AI-powered semantic layer for SAP-style enterprise analytics, process mining, and KPI intelligence.

PrimeConSemLayer provides a full-stack platform to:
- Translate natural language questions into safe SQL
- Query SAP-like business datasets and visualize results
- Generate prompt-driven dashboards
- Run process mining (DFG/Petri-net style outputs)
- Track 19 KPIs and generate root-cause analysis

## Tech Stack
- Frontend: React, Vite, TypeScript, Tailwind, Recharts, React Flow
- Backend: FastAPI, SQLAlchemy, LangChain, Gemini (`langchain-google-genai`)
- Data/Infra: SQLite (seeded SAP-style mock), Redis, ChromaDB, Docker Compose
- Process Mining: `pm4py` with deterministic fallback logic

## Repository Structure
```text
primecon/
├─ frontend/                 # React UI
├─ backend/                  # FastAPI services + models + routers
│  ├─ routers/               # Query/KPI/Mining/Dashboard APIs
│  ├─ services/              # NL engine, mining, RCA, KPI computation, charting
│  ├─ data/                  # Catalog and local DB artifacts
│  └─ tests/                 # Unit + integration eval suite
├─ docker-compose.yml
└─ .env / .env.example
```

## Core Modules

### 1) Natural Language Query Engine
- `POST /api/query`
- `POST /api/query/stream`
- Converts prompt -> SQL (deterministic planner first, LLM for complex prompts)
- SQL safety guardrails block destructive/invalid statements
- Returns:
  - SQL text
  - rows/columns
  - chart recommendation
  - AI summary (or deterministic fallback on quota issues)

### 2) NL Dashboard Builder
- `POST /api/dashboard/generate`
- Generates 4-panel dashboards from prompts
- Supports fallback panel generation when LLM is unavailable/quota-limited

### 3) Process Mining
- `GET /api/mining/sources`
- `POST /api/mining/discover` (DFG)
- `POST /api/mining/petri` (Petri-style)
- Outputs process graph, conformance, performance metrics, bottleneck signals

### 4) KPI Dashboard + RCA
- `GET /api/kpi/all`
- `GET /api/kpi/modules`
- `GET /api/kpi/rca/{kpi_id}`
- Tracks 19 KPIs across FI/SD/MM/PP
- Root cause analysis supports LLM mode + deterministic fallback

## Prerequisites
- Docker Desktop (with Docker Compose)
- 8GB+ RAM recommended
- Gemini API key (`GOOGLE_API_KEY`) if using live LLM behavior

## Configuration

Create `.env` in project root:

```env
GOOGLE_API_KEY=your_google_api_key
REDIS_URL=redis://redis:6379/0
CHROMA_HOST=chromadb
CHROMA_PORT=8000
DATABASE_URL=sqlite:////app/data/sap_mock.db
MOCK_MODE=false
ENVIRONMENT=development
LOG_LEVEL=info
```

### `MOCK_MODE` Guidance
- `MOCK_MODE=true`: fastest deterministic demo mode (no LLM dependency)
- `MOCK_MODE=false`: LLM-enabled mode with automatic deterministic fallback on quota failure

## Quick Start (Docker)

```bash
docker-compose up --build
```

App URLs:
- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend: [http://localhost:8000](http://localhost:8000)
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Health & Diagnostics

```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/llm
```

`/health/llm` helps confirm model availability and quota condition.

## Testing

Unit/eval suite:
```bash
cd backend
pytest -q tests/test_nl_eval_suite.py
```

Integration tests (requires backend running):
```bash
cd backend
pytest -q tests/test_api_integration.py -m integration -vv
```

## Example Prompts
- `Show revenue by customer`
- `Top 5 overdue invoices`
- `Sales orders created this week`
- `Inventory value by plant`
- `Create a procurement performance dashboard for vendor and PO metrics`
- `Show a production health dashboard with schedule adherence and late orders`

## Known Runtime Behavior
- If Gemini quota is exhausted, the system switches to deterministic fallback responses for stability.
- Process mining runs with `pm4py`; if library-level discovery fails, deterministic fallback logic is used.

## Production Hardening Roadmap
- SAP ECC/S4HANA live connectors (PyRFC/OData adapters)
- AuthN/AuthZ (RBAC), audit trails, secret management
- CI/CD quality gates and load/security testing
- Advanced anomaly detection and evidence-backed RCA scoring
- Monitoring/observability (OpenTelemetry, dashboards, alerting)

## License
Internal/Proprietary (update as needed).
