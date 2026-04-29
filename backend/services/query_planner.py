from typing import Dict

# Deterministic semantic planner for high-confidence enterprise intents.
# This avoids hallucinations and is used as primary fallback or quota-safe route.
INTENT_SQL: Dict[str, str] = {
    "revenue_by_customer": "SELECT kunnr, sum(netwr) as revenue FROM vbak GROUP BY kunnr ORDER BY revenue DESC LIMIT 10",
    "top_overdue_invoices": (
        "SELECT bseg.belnr as belnr, bkpf.budat as budat, bseg.dmbtr as dmbtr "
        "FROM bseg JOIN bkpf ON bseg.belnr = bkpf.belnr "
        "WHERE bkpf.budat < date((SELECT max(budat) FROM bkpf), '-45 days') "
        "ORDER BY bseg.dmbtr DESC LIMIT 5"
    ),
    "open_ap": "SELECT belnr, dmbtr, shkzg FROM bseg WHERE shkzg = 'H' ORDER BY dmbtr DESC LIMIT 20",
    "inventory_by_plant": "SELECT werks as plant, sum(dmbtr) as inventory_value FROM mseg GROUP BY werks ORDER BY inventory_value DESC",
    "sales_this_week": (
        "SELECT vbeln, erdat, kunnr, netwr FROM vbak "
        "WHERE erdat >= date((SELECT max(erdat) FROM vbak), '-7 days') "
        "ORDER BY erdat DESC LIMIT 20"
    ),
    "top_sales_orders": "SELECT vbeln, kunnr, erdat, netwr FROM vbak ORDER BY netwr DESC LIMIT 20",
    "purchase_orders": (
        "SELECT ekko.ebeln, ekko.lifnr, ekko.bedat, sum(ekpo.netpr) as total "
        "FROM ekko JOIN ekpo ON ekko.ebeln = ekpo.ebeln "
        "GROUP BY ekko.ebeln, ekko.lifnr, ekko.bedat ORDER BY total DESC LIMIT 20"
    ),
    "purchase_without_gr": (
        "SELECT ekko.ebeln, ekko.lifnr, ekko.bedat "
        "FROM ekko LEFT JOIN mseg ON mseg.ebeln = ekko.ebeln "
        "WHERE mseg.ebeln IS NULL LIMIT 20"
    ),
    "delayed_production": "SELECT aufnr, matnr, werks, gstrs, gltrs, getri FROM aufk WHERE getri > gltrs ORDER BY getri DESC LIMIT 20",
    "default_orders": "SELECT vbeln, erdat, kunnr, netwr FROM vbak ORDER BY erdat DESC LIMIT 20",
}


def plan_question_to_sql(question: str) -> str:
    q = question.lower().strip()

    if ("revenue" in q or "sales" in q) and "customer" in q:
        return INTENT_SQL["revenue_by_customer"]
    if "overdue" in q and ("invoice" in q or "ap" in q or "ar" in q):
        return INTENT_SQL["top_overdue_invoices"]
    if "open" in q and "ap" in q:
        return INTENT_SQL["open_ap"]
    if "inventory" in q and "plant" in q:
        return INTENT_SQL["inventory_by_plant"]
    if "sales" in q and "week" in q:
        return INTENT_SQL["sales_this_week"]
    if "top" in q and ("sales order" in q or "orders" in q):
        return INTENT_SQL["top_sales_orders"]
    if "purchase" in q and "without goods" in q:
        return INTENT_SQL["purchase_without_gr"]
    if "purchase" in q and "order" in q:
        return INTENT_SQL["purchase_orders"]
    if "production" in q and ("late" in q or "delay" in q):
        return INTENT_SQL["delayed_production"]
    if "pending" in q and "order" in q:
        return INTENT_SQL["default_orders"]
    if "show orders" in q or "orders" in q:
        return INTENT_SQL["default_orders"]

    return "SELECT 1 as mock_result"
