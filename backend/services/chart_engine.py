def is_numeric(value):
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def recommend_chart(columns, rows, row_count) -> dict:
    if not columns or not rows:
        return {"type": "DataTable", "data": [], "config": {"height": 280}}

    date_patterns = ["month", "date", "period", "year", "week", "erdat", "budat", "bldat"]
    
    if len(columns) == 2:
        col0_is_date = any(p in columns[0].lower() for p in date_patterns)
        col1_is_numeric = is_numeric(rows[0][1])
        
        if col0_is_date and col1_is_numeric:
            return {"type": "LineChart", "data": [], "config": {"xKey": columns[0], "yKey": columns[1], "color": "#6366f1", "height": 280}}
        elif col1_is_numeric and row_count <= 6:
            return {"type": "PieChart", "data": [], "config": {"nameKey": columns[0], "valueKey": columns[1], "height": 280}}
        elif col1_is_numeric and row_count > 6:
            return {"type": "BarChart", "data": [], "config": {"xKey": columns[0], "yKey": columns[1], "color": "#10b981", "height": 280}}
            
    if len(columns) >= 3:
        # For identifier/date/value result sets (common in "top N" style queries),
        # table view is usually clearer than an auto-composed chart.
        has_id_like_col = any(c.lower() in ["vbeln", "belnr", "kunnr", "matnr", "ebeln", "aufnr"] for c in columns)
        has_date_col = any(any(p in c.lower() for p in date_patterns) for c in columns)
        numeric_count = sum(1 for i, _ in enumerate(columns) if is_numeric(rows[0][i]))
        if has_id_like_col and has_date_col and numeric_count <= 1:
            return {"type": "DataTable", "data": [], "config": {"height": 280}}

        date_col = next((c for c in columns if any(p in c.lower() for p in date_patterns)), None)
        numeric_cols = [c for i, c in enumerate(columns) if is_numeric(rows[0][i]) and c != date_col]
        if date_col and len(numeric_cols) >= 1:
            return {"type": "ComposedChart", "data": [], "config": {"xKey": date_col, "yKeys": numeric_cols, "height": 280}}
            
    return {"type": "DataTable", "data": [], "config": {"height": 280}}
