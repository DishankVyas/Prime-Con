import re
from typing import Dict, Set, Tuple

ALLOWED_TABLES: Dict[str, Set[str]] = {
    "vbak": {"vbeln", "erdat", "kunnr", "netwr", "auart", "waerk"},
    "vbap": {"vbeln", "posnr", "matnr", "arktx", "kwmeng", "netpr", "werks"},
    "bkpf": {"bukrs", "belnr", "gjahr", "blart", "bldat", "budat", "xblnr", "waers"},
    "bseg": {"bukrs", "belnr", "gjahr", "buzei", "hkont", "shkzg", "dmbtr", "wrbtr"},
    "ekko": {"ebeln", "bukrs", "lifnr", "bedat", "bsart", "waers"},
    "ekpo": {"ebeln", "ebelp", "matnr", "txz01", "menge", "netpr", "eindt"},
    "mseg": {"mblnr", "mjahr", "zeile", "bwart", "matnr", "werks", "menge", "dmbtr", "ebeln"},
    "aufk": {"aufnr", "auart", "matnr", "werks", "gamng", "gstrs", "gltrs", "getri", "igmng"},
    "cdhdr": {"changenr", "objectclas", "udate", "tcode"},
    "cdpos": {"changenr", "tabname", "fname", "chngind", "value_new", "value_old"},
}

FORBIDDEN_SQL = (
    "drop ",
    "delete ",
    "update ",
    "insert ",
    "alter ",
    "create ",
    "attach ",
    "detach ",
    "pragma ",
    "truncate ",
)


def _table_alias_map(sql: str) -> Dict[str, str]:
    alias_map: Dict[str, str] = {}
    pattern = re.compile(
        r"\b(from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:as\s+)?([a-zA-Z_][a-zA-Z0-9_]*)?",
        re.IGNORECASE,
    )
    for _, table, alias in pattern.findall(sql):
        t = table.lower()
        if t in ALLOWED_TABLES:
            alias_map[t] = t
            if alias:
                alias_map[alias.lower()] = t
    return alias_map


def _validate_tables(sql: str) -> Tuple[bool, str]:
    pattern = re.compile(r"\b(from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.IGNORECASE)
    tables = [t.lower() for _, t in pattern.findall(sql)]
    if not tables:
        return False, "No FROM/JOIN table found."
    for table in tables:
        if table not in ALLOWED_TABLES:
            return False, f"Table not allowed: {table}"
    return True, ""


def _validate_qualified_columns(sql: str) -> Tuple[bool, str]:
    aliases = _table_alias_map(sql)
    # Validate alias.column references. Keep this strict and deterministic.
    for alias, col in re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\b", sql):
        a = alias.lower()
        c = col.lower()
        if a in {"date", "strftime", "sum", "avg", "count", "min", "max", "julianday", "cast"}:
            continue
        if a not in aliases:
            return False, f"Unknown alias/table qualifier: {alias}"
        real_table = aliases[a]
        if c not in ALLOWED_TABLES[real_table]:
            return False, f"Unknown column {alias}.{col}"
    return True, ""


def validate_select_sql(sql: str) -> Tuple[bool, str]:
    if not sql or not sql.strip():
        return False, "Empty SQL."

    normalized = " ".join(sql.strip().split())
    lower_sql = normalized.lower()

    if ";" in normalized.rstrip(";"):
        return False, "Multiple statements are not allowed."

    if not (lower_sql.startswith("select ") or lower_sql.startswith("with ")):
        return False, "Only SELECT/CTE SELECT queries are allowed."

    for token in FORBIDDEN_SQL:
        if token in f" {lower_sql} ":
            return False, f"Forbidden SQL operation detected: {token.strip()}"

    ok, reason = _validate_tables(lower_sql)
    if not ok:
        return False, reason

    ok, reason = _validate_qualified_columns(lower_sql)
    if not ok:
        return False, reason

    return True, ""
