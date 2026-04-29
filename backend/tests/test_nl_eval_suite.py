import pytest

from services.query_planner import plan_question_to_sql
from services.sql_guard import validate_select_sql


TEST_CASES = [
    "Show revenue by customer",
    "Top 5 overdue invoices",
    "Open AP amounts by vendor",
    "Inventory value by plant",
    "Delayed production orders",
    "Sales orders created this week",
    "Purchase orders without goods receipt",
]


@pytest.mark.parametrize("question", TEST_CASES)
def test_planner_returns_safe_select(question: str):
    sql = plan_question_to_sql(question)
    ok, reason = validate_select_sql(sql)
    assert ok, f"{question}: {reason}"
    assert sql.lower().startswith(("select", "with"))


def test_rejects_destructive_sql():
    ok, _ = validate_select_sql("DROP TABLE vbak")
    assert not ok


def test_rejects_unknown_tables():
    ok, _ = validate_select_sql("SELECT * FROM users")
    assert not ok
