import time
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import text
from config import settings
from database import get_session
from services.sap_connector import get_connector
import hashlib
import json
import redis as redis_client

def _get_redis():
    try:
        r = redis_client.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=2)
        r.ping()
        return r
    except Exception:
        return None
from services.embedding_service import embedding_service
from services.chart_engine import recommend_chart
from services.query_planner import plan_question_to_sql
from services.sql_guard import validate_select_sql

_llm_instance = None
_llm_quota_blocked_until = 0.0


def _is_quota_error(err: Exception) -> bool:
    msg = str(err).lower()
    return (
        "resourceexhausted" in msg
        or "quota exceeded" in msg
        or "429" in msg
        or "rate limit" in msg
    )


def _is_llm_temporarily_blocked() -> bool:
    return time.time() < _llm_quota_blocked_until


def _block_llm_for(seconds: int = 3600) -> None:
    global _llm_quota_blocked_until
    _llm_quota_blocked_until = time.time() + max(seconds, 30)

def _get_llm():
    global _llm_instance
    if _llm_instance is None:
        from langchain_google_genai import ChatGoogleGenerativeAI
        _llm_instance = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0,
            max_retries=0,
        )
    return _llm_instance

MOCK_QUERIES = {
    "show revenue": "SELECT sum(netwr) as revenue FROM vbak",
    "revenue by customer": "SELECT kunnr, sum(netwr) as revenue FROM vbak GROUP BY kunnr ORDER BY revenue DESC LIMIT 10",
    "top customers": "SELECT kunnr, sum(netwr) as revenue FROM vbak GROUP BY kunnr ORDER BY revenue DESC LIMIT 5",
    "top 5 overdue": "SELECT bseg.belnr as belnr, bkpf.budat as budat, bseg.dmbtr as dmbtr FROM bseg JOIN bkpf ON bseg.belnr = bkpf.belnr WHERE bkpf.budat < date('now', '-45 days') ORDER BY bseg.dmbtr DESC LIMIT 5",
    "overdue invoices": "SELECT bseg.belnr as belnr, bkpf.budat as budat, bseg.dmbtr as dmbtr FROM bseg JOIN bkpf ON bseg.belnr = bkpf.belnr WHERE bkpf.budat < date('now', '-45 days') LIMIT 20",
    "open ap": "SELECT belnr, dmbtr, shkzg FROM bseg WHERE shkzg = 'H' ORDER BY dmbtr DESC LIMIT 10",
    "inventory value": "SELECT matnr, sum(menge) as qty, sum(dmbtr) as val FROM mseg GROUP BY matnr ORDER BY val DESC LIMIT 10",
    "inventory value by plant": "SELECT werks as plant, sum(dmbtr) as inventory_value FROM mseg GROUP BY werks ORDER BY inventory_value DESC",
    "purchase orders": "SELECT ekko.ebeln, lifnr, sum(netpr) as total FROM ekko JOIN ekpo ON ekko.ebeln = ekpo.ebeln GROUP BY ekko.ebeln ORDER BY total DESC LIMIT 10",
    "highest value purchase": "SELECT ekko.ebeln, ekko.lifnr, sum(ekpo.netpr) as total_value FROM ekko JOIN ekpo ON ekko.ebeln = ekpo.ebeln GROUP BY ekko.ebeln ORDER BY total_value DESC LIMIT 5",
    "purchase orders without goods": "SELECT ekko.ebeln, ekko.lifnr, ekko.bedat FROM ekko LEFT JOIN mseg ON mseg.ebeln = ekko.ebeln WHERE mseg.ebeln IS NULL LIMIT 20",
    "delayed production": "SELECT aufnr, gstrs, gltrs, getri FROM aufk WHERE getri > gltrs LIMIT 20",
    "production delay": "SELECT aufnr, gstrs, gltrs, getri FROM aufk WHERE getri > gltrs LIMIT 20",
    "sales this month": "SELECT erdat, sum(netwr) as sales FROM vbak GROUP BY erdat ORDER BY erdat DESC",
    "sales orders this week": "SELECT vbeln, erdat, kunnr, netwr FROM vbak ORDER BY erdat DESC LIMIT 20",
    "open items": "SELECT belnr, dmbtr FROM bseg WHERE shkzg = 'S' LIMIT 20",
    "scrap rate by material": "SELECT matnr, COUNT(*) as production_orders, SUM(CASE WHEN igmng < gamng THEN 1 ELSE 0 END) as underperforming FROM aufk GROUP BY matnr ORDER BY underperforming DESC LIMIT 10",
    "vendor on-time": "SELECT COUNT(*) as total_pos FROM ekko",
    "returned items": "SELECT matnr, COUNT(*) as returns FROM vbap JOIN vbak ON vbap.vbeln = vbak.vbeln WHERE vbak.auart = 'RE' GROUP BY matnr ORDER BY returns DESC LIMIT 10",
    "average order to cash": "SELECT AVG(CAST(julianday(budat) - julianday(bldat) AS REAL)) as avg_otc_days FROM bkpf WHERE budat > bldat",
    "dashboard": "SELECT 'DSO' as kpi, 42.5 as value, 'days' as unit UNION ALL SELECT 'Revenue' as kpi, 850000 as value, 'EUR' as unit UNION ALL SELECT 'Overdue' as kpi, 3000 as value, 'count' as unit UNION ALL SELECT 'OEE' as kpi, 72.4 as value, '%' as unit",
    "summary": "SELECT 'DSO' as kpi, 42.5 as value, 'days' as unit UNION ALL SELECT 'Revenue' as kpi, 850000 as value, 'EUR' as unit UNION ALL SELECT 'Cancel Rate' as kpi, 8.1 as value, '%' as unit UNION ALL SELECT 'Schedule Adherence' as kpi, 87.9 as value, '%' as unit",
}

def _fallback_sql_for_question(question: str) -> str:
    q = question.lower().strip()
    for key, val in MOCK_QUERIES.items():
        if key in q:
            return val

    # Fuzzy keyword fallback to avoid SELECT 1 for common phrasing
    if "revenue" in q and "customer" in q:
        return MOCK_QUERIES["revenue by customer"]
    if "overdue" in q or "invoice" in q:
        return MOCK_QUERIES["overdue invoices"]
    if "inventory" in q and "plant" in q:
        return MOCK_QUERIES["inventory value by plant"]
    if "purchase" in q and "order" in q:
        return MOCK_QUERIES["purchase orders"]
    if "pending" in q and "order" in q:
        return "SELECT vbeln, erdat, kunnr, netwr FROM vbak ORDER BY erdat DESC LIMIT 20"
    if "open" in q and "order" in q:
        return "SELECT vbeln, erdat, kunnr, netwr FROM vbak ORDER BY erdat DESC LIMIT 20"
    if "production" in q and ("delay" in q or "late" in q):
        return MOCK_QUERIES["delayed production"]
    if "sales" in q and "week" in q:
        return MOCK_QUERIES["sales orders this week"]
    if "scrap" in q:
        return MOCK_QUERIES["scrap rate by material"]
    if "vendor" in q and "time" in q:
        return MOCK_QUERIES["vendor on-time"]
    if "return" in q:
        return MOCK_QUERIES["returned items"]
    if "open" in q and "ap" in q:
        return MOCK_QUERIES["open ap"]

    return "SELECT 1 as mock_result"

async def generate_summary(question: str, data: list) -> str:
    if not data:
        return "No data found for this query."

    # In MOCK_MODE skip the LLM call entirely — return instant summary
    if settings.MOCK_MODE:
        row_count = len(data)
        first_row = data[0] if data else {}
        cols = list(first_row.keys())
        if len(cols) >= 2:
            col1, col2 = cols[0], cols[1]
            top_val = first_row.get(col2, '')
            return (
                f"Query returned {row_count} rows. "
                f"Top result: {col1}={first_row.get(col1, 'N/A')}, "
                f"{col2}={top_val}. "
                f"Showing {min(row_count, 10)} of {row_count} records."
            )
        return f"Query completed successfully. {row_count} records retrieved."

    # Only call LLM when not in MOCK_MODE
    try:
        if _is_llm_temporarily_blocked():
            raise RuntimeError("LLM temporarily blocked due to prior quota exhaustion")
        prompt = ChatPromptTemplate.from_template(
            "You are a SAP business analyst. In 2 sentences, summarize what this data shows. "
            "Question: {question}\nData (first 5 rows): {data}"
        )
        chain = prompt | _get_llm()
        res = await chain.ainvoke({"question": question, "data": str(data[:5])})
        return res.content
    except Exception as e:
        if _is_quota_error(e):
            _block_llm_for(3600)
            row_count = len(data)
            return f"Gemini quota exceeded. Returning SQL result only ({row_count} rows)."
        return f"Query returned {len(data)} rows successfully."

def validate_sql(sql: str) -> bool:
    ok, _ = validate_select_sql(sql)
    return ok

async def execute_nl_query(question: str) -> dict:
    start_time = time.time()
    
    # Cache check — skip for non-MOCK_MODE (LLM results should be fresh)
    cache_key = f"query:v2:{hashlib.md5(question.lower().strip().encode()).hexdigest()}"
    r = _get_redis()
    if r and settings.MOCK_MODE:
        cached = r.get(cache_key)
        if cached:
            try:
                result = json.loads(cached)
                result["from_cache"] = True
                return result
            except Exception:
                pass
    
    if settings.MOCK_MODE:
        sql = plan_question_to_sql(question)
    else:
        # Deterministic planner-first route for known intents.
        # This avoids unnecessary LLM latency and quota dependency for common SAP questions.
        planned_sql = plan_question_to_sql(question)
        if planned_sql.strip().lower() != "select 1 as mock_result":
            sql = planned_sql
        elif _is_llm_temporarily_blocked():
            sql = plan_question_to_sql(question)
        else:
            SCHEMA_FALLBACK = """
Tables in SQLite database:
- vbak(vbeln PK, erdat DATE, kunnr VARCHAR, netwr FLOAT, auart VARCHAR, waerk VARCHAR)  -- Sales orders
- vbap(vbeln FK, posnr, matnr, arktx, kwmeng FLOAT, netpr FLOAT, werks)  -- Sales order items
- bkpf(bukrs, belnr PK, gjahr, blart, bldat DATE, budat DATE, xblnr, waers)  -- FI documents
- bseg(bukrs, belnr, gjahr, buzei PK, hkont, shkzg, dmbtr FLOAT, wrbtr FLOAT)  -- FI line items
- ekko(ebeln PK, bukrs, lifnr, bedat DATE, bsart, waers)  -- Purchase orders
- ekpo(ebeln FK, ebelp PK, matnr, txz01, menge FLOAT, netpr FLOAT, eindt DATE)  -- PO items
- mseg(mblnr, mjahr, zeile PK, bwart, matnr, werks, menge FLOAT, dmbtr FLOAT, ebeln)  -- Material movements
- aufk(aufnr PK, auart, matnr, werks, gamng FLOAT, gstrs DATE, gltrs DATE, getri DATE, igmng FLOAT)  -- Production orders
- cdhdr(changenr PK, objectclas, udate DATE, tcode)  -- Change document headers
- cdpos(changenr FK, tabname, fname, chngind, value_new, value_old)  -- Change document items

Key joins: vbap.vbeln=vbak.vbeln | bseg.belnr=bkpf.belnr | ekpo.ebeln=ekko.ebeln
Use date() and julianday() for SQLite date arithmetic.
"""
            try:
                context = await asyncio.wait_for(
                    embedding_service.retrieve_schema_context(question),
                    timeout=8
                ) or SCHEMA_FALLBACK
            except Exception:
                context = SCHEMA_FALLBACK
            prompt = ChatPromptTemplate.from_template(
                "You are a SQLite expert for SAP data. Return ONLY a valid SELECT statement, no markdown, no explanation.\n"
                "Schema:\n{context}\n\n"
                "Question: {question}\n\n"
                "SQL:"
            )
            chain = prompt | _get_llm()
            try:
                response = await asyncio.wait_for(
                    chain.ainvoke({"context": context, "question": question}),
                    timeout=15
                )
                sql = response.content.replace("```sql", "").replace("```", "").strip()
                if not validate_sql(sql):
                    raise Exception("Invalid SQL")
            except Exception as e:
                if _is_quota_error(e):
                    _block_llm_for(3600)
                # fallback to deterministic local mapping
                sql = plan_question_to_sql(question)

    is_valid, validation_error = validate_select_sql(sql)
    if not is_valid:
        return {"error": f"Invalid SQL generated: {validation_error}"}

    print(f"Executing SQL: {sql}")
    
    try:
        def fetch_data():
            rows_dict = get_connector().execute_query(sql)
            if not rows_dict:
                return [], []
            cols = list(rows_dict[0].keys())
            rows_list = [list(r.values()) for r in rows_dict]
            return cols, rows_list
                
        columns, rows = await asyncio.to_thread(fetch_data)

        # If a strict "this week" SQL returns no rows against older seeded data, fall back to latest orders.
        if (not rows) and ("date('now', '-7 days')" in sql.lower()) and ("from vbak" in sql.lower()):
            fallback_sql = "SELECT vbeln, erdat, kunnr, netwr FROM vbak ORDER BY erdat DESC LIMIT 20"
            rows_dict = get_connector().execute_query(fallback_sql)
            if rows_dict:
                sql = fallback_sql
                columns = list(rows_dict[0].keys())
                rows = [list(r.values()) for r in rows_dict]
    except Exception as e:
        return {"error": str(e)}

    execution_time_ms = round((time.time() - start_time) * 1000, 2)
    row_count = len(rows)

    # Build data list of dicts FIRST
    data = [dict(zip(columns, row)) for row in rows]

    # Get chart config and inject real data into it
    chart_config = recommend_chart(columns, rows, row_count)
    chart_config["data"] = data  # FIX: was always empty []

    # Generate AI summary with correct args
    summary = await generate_summary(question, data)  # FIX: was passing columns as question

    result = {
        "question": question,
        "sql": sql,
        "columns": columns,
        "rows": rows,
        "row_count": row_count,
        "chart_config": chart_config,
        "data": data,
        "execution_time_ms": execution_time_ms,
        "ai_summary": summary,
        "llm_enabled": not settings.MOCK_MODE,
    }

    # Cache the result before returning (TTL: 5 minutes for mock data)
    if r and settings.MOCK_MODE:
        try:
            r.setex(cache_key, 300, json.dumps(result, default=str))
        except Exception:
            pass

    return result
