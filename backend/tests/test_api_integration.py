import os
import pytest
import httpx


BASE_URL = os.getenv("PRIMECON_API_URL", "http://localhost:8000")


@pytest.mark.integration
def test_health_endpoint():
    r = httpx.get(f"{BASE_URL}/health", timeout=10)
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "ok"


@pytest.mark.integration
@pytest.mark.parametrize(
    "question",
    [
        "Show revenue by customer",
        "Top 5 overdue invoices",
        "Inventory value by plant",
    ],
)
def test_query_endpoint(question: str):
    r = httpx.post(
        f"{BASE_URL}/api/query",
        json={"question": question},
        timeout=30,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "sql" in body and body["sql"].lower().startswith(("select", "with"))
    assert "rows" in body and isinstance(body["rows"], list)
