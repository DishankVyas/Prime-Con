import json
import asyncio
from langchain_core.prompts import ChatPromptTemplate
from services.nl_engine import _get_llm
from services.sap_connector import get_connector
from config import settings


def _is_quota_error(err: Exception) -> bool:
    msg = str(err).lower()
    return (
        "resourceexhausted" in msg
        or "quota exceeded" in msg
        or "429" in msg
        or "rate limit" in msg
    )

def _get_mock_panels_for_prompt(prompt: str) -> list:
    """Return relevant mock panels based on keywords in the prompt."""
    p = prompt.lower()

    # Prioritize specific domain intents before generic "order"/"sales" tokens
    if any(k in p for k in ['production', 'manufacturing', 'plant', 'oee']):
        return [
            {"title": "Production by Plant", "sql": "SELECT werks, COUNT(*) as orders, SUM(gamng) as planned_qty, SUM(igmng) as actual_qty FROM aufk GROUP BY werks", "chart_type": "BarChart"},
            {"title": "Schedule Adherence Trend", "sql": "SELECT strftime('%Y-%m', gstrs) as month, COUNT(*) as total, SUM(CASE WHEN getri <= gltrs THEN 1 ELSE 0 END) as on_time FROM aufk GROUP BY month ORDER BY month", "chart_type": "LineChart"},
            {"title": "Order Status", "sql": "SELECT aueru, COUNT(*) as count FROM aufk GROUP BY aueru", "chart_type": "PieChart"},
            {"title": "Late Production Orders", "sql": "SELECT aufnr, matnr, werks, gltrs, getri FROM aufk WHERE getri > gltrs ORDER BY getri DESC LIMIT 20", "chart_type": "DataTable"},
        ]
    elif any(k in p for k in ['purchase', 'vendor', 'procurement', 'pay']):
        return [
            {"title": "PO Value by Vendor", "sql": "SELECT ekko.lifnr, SUM(ekpo.netpr * ekpo.menge) as total FROM ekko JOIN ekpo ON ekko.ebeln=ekpo.ebeln GROUP BY ekko.lifnr ORDER BY total DESC LIMIT 10", "chart_type": "BarChart"},
            {"title": "Monthly PO Volume", "sql": "SELECT strftime('%Y-%m', bedat) as month, COUNT(*) as pos, SUM(ekpo.netpr) as value FROM ekko JOIN ekpo ON ekko.ebeln=ekpo.ebeln GROUP BY month ORDER BY month", "chart_type": "LineChart"},
            {"title": "PO by Type", "sql": "SELECT bsart, COUNT(*) as count FROM ekko GROUP BY bsart", "chart_type": "PieChart"},
            {"title": "Recent Purchase Orders", "sql": "SELECT ekko.ebeln, ekko.lifnr, ekko.bedat, SUM(ekpo.netpr) as value FROM ekko JOIN ekpo ON ekko.ebeln=ekpo.ebeln GROUP BY ekko.ebeln ORDER BY ekko.bedat DESC LIMIT 20", "chart_type": "DataTable"},
        ]
    elif any(k in p for k in ['finance', 'fi', 'invoice', 'payable', 'receivable', 'kpi']):
        return [
            {"title": "Open AR by Account", "sql": "SELECT hkont, SUM(dmbtr) as amount FROM bseg WHERE shkzg='S' GROUP BY hkont ORDER BY amount DESC LIMIT 10", "chart_type": "BarChart"},
            {"title": "Posting Volume by Month", "sql": "SELECT strftime('%Y-%m', budat) as month, COUNT(*) as docs, SUM(dmbtr) as amount FROM bkpf GROUP BY month ORDER BY month", "chart_type": "LineChart"},
            {"title": "Document Types", "sql": "SELECT blart, COUNT(*) as count FROM bkpf GROUP BY blart ORDER BY count DESC", "chart_type": "PieChart"},
            {"title": "Overdue Invoices", "sql": "SELECT belnr, budat, waers, dmbtr FROM bkpf WHERE budat < date('now', '-30 days') ORDER BY dmbtr DESC LIMIT 20", "chart_type": "DataTable"},
        ]
    elif any(k in p for k in ['order', 'cash', 'revenue', 'sales', 'customer']):
        return [
            {"title": "Revenue by Customer", "sql": "SELECT kunnr, SUM(netwr) as revenue FROM vbak GROUP BY kunnr ORDER BY revenue DESC LIMIT 10", "chart_type": "BarChart"},
            {"title": "Monthly Sales Trend", "sql": "SELECT strftime('%Y-%m', erdat) as month, SUM(netwr) as revenue FROM vbak GROUP BY month ORDER BY month", "chart_type": "LineChart"},
            {"title": "Orders by Type", "sql": "SELECT auart, COUNT(*) as count, SUM(netwr) as value FROM vbak GROUP BY auart", "chart_type": "PieChart"},
            {"title": "Top Sales Orders", "sql": "SELECT vbeln, kunnr, erdat, netwr FROM vbak ORDER BY netwr DESC LIMIT 20", "chart_type": "DataTable"},
        ]
    else:
        # Default: general SAP overview
        return [
            {"title": "Revenue by Customer", "sql": "SELECT kunnr, SUM(netwr) as revenue FROM vbak GROUP BY kunnr ORDER BY revenue DESC LIMIT 10", "chart_type": "BarChart"},
            {"title": "Overdue Invoices", "sql": "SELECT belnr, budat, dmbtr FROM bkpf WHERE budat < date('now', '-30 days') ORDER BY dmbtr DESC LIMIT 10", "chart_type": "DataTable"},
            {"title": "AP vs AR", "sql": "SELECT shkzg, SUM(dmbtr) as amount FROM bseg GROUP BY shkzg", "chart_type": "PieChart"},
            {"title": "Inventory by Plant", "sql": "SELECT werks, SUM(dmbtr) as inventory_value FROM mseg GROUP BY werks ORDER BY inventory_value DESC", "chart_type": "BarChart"},
        ]


async def _execute_panels(panels_config: list) -> dict:
    """Execute SQL for each panel and return structured dashboard response."""
    async def process_panel(panel):
        try:
            def fetch():
                return get_connector().execute_query(panel["sql"])
            rows = await asyncio.to_thread(fetch)
            return {**panel, "data": rows or []}
        except Exception as e:
            return {**panel, "data": [], "error": str(e)}

    results = await asyncio.gather(*(process_panel(p) for p in panels_config))

    final_panels = []
    for r in results:
        first_row = r["data"][0] if r["data"] else {}
        keys = list(first_row.keys()) if first_row else ["label", "value"]
        final_panels.append({
            "title": r["title"],
            "chart_config": {
                "type": r["chart_type"],
                "config": {
                    "xKey": keys[0] if len(keys) > 0 else "label",
                    "yKey": keys[1] if len(keys) > 1 else "value",
                    "valueKey": keys[1] if len(keys) > 1 else "value",
                    "nameKey": keys[0] if len(keys) > 0 else "label",
                },
            },
            "data": r["data"],
            "sql": r["sql"],
            "error": r.get("error"),
        })

    return {"panels": final_panels}


async def generate_dashboard(prompt: str) -> dict:
    # In MOCK_MODE, skip LLM entirely — instant response with keyword-matched panels
    if settings.MOCK_MODE:
        return await _execute_panels(_get_mock_panels_for_prompt(prompt))

    panels_config = None
    try:
        llm = _get_llm()
        template = """
You are a SAP analytics expert. The user wants: "{prompt}"
Return ONLY a JSON array of 4 dashboard panels. Each panel:
{{"title": "...", "sql": "SELECT ... FROM ...", "chart_type": "LineChart|BarChart|PieChart|DataTable"}}
Use only these tables: vbak, vbap, bkpf, bseg, ekko, ekpo, mseg, aufk
Return raw JSON array only, no markdown, no explanation.
"""
        chat_prompt = ChatPromptTemplate.from_template(template)
        chain = chat_prompt | llm
        response = await asyncio.wait_for(chain.ainvoke({"prompt": prompt}), timeout=10)
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        panels_config = json.loads(content)
        if not isinstance(panels_config, list):
            panels_config = None
    except Exception as e:
        if _is_quota_error(e):
            print("[DashboardService] Gemini quota exceeded, using deterministic fallback panels")
        else:
            print(f"[DashboardService] LLM failed ({e}), using fallback panels")
        panels_config = None

    if panels_config is None:
        panels_config = _get_mock_panels_for_prompt(prompt)

    return await _execute_panels(panels_config)
