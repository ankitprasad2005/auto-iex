def test_read_billing_history_empty(client):
    resp = client.get("/billing/history")
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"records": [], "total_kwh": "0", "total_cost_rs": "0"}


def test_load_demo_billing_populates_history(client):
    resp = client.post("/billing/demo")
    assert resp.status_code == 200
    body = resp.json()
    assert body["created_count"] > 0

    history_resp = client.get("/billing/history")
    history = history_resp.json()
    assert len(history["records"]) == body["created_count"]
    assert float(history["total_cost_rs"]) > 0
    assert float(history["total_kwh"]) > 0

    record = history["records"][0]
    assert set(record.keys()) == {"date", "time_label", "market", "kwh", "cost_rs"}


def test_reloading_demo_billing_replaces_rather_than_duplicates(client):
    first = client.post("/billing/demo").json()
    second = client.post("/billing/demo").json()
    assert first["created_count"] == second["created_count"]

    history = client.get("/billing/history").json()
    assert len(history["records"]) == second["created_count"]
