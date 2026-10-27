def test_get_rtm_interval_returns_the_default(client):
    resp = client.get("/scheduler/rtm-interval")
    assert resp.status_code == 200
    assert resp.json() == {"seconds": 30}


def test_update_rtm_interval_changes_it(client):
    resp = client.patch("/scheduler/rtm-interval", json={"seconds": 120})
    assert resp.status_code == 200
    assert resp.json() == {"seconds": 120}

    resp2 = client.get("/scheduler/rtm-interval")
    assert resp2.json() == {"seconds": 120}


def test_update_rtm_interval_rejects_too_small_a_value(client):
    resp = client.patch("/scheduler/rtm-interval", json={"seconds": 5})
    assert resp.status_code == 422


def test_update_rtm_interval_accepts_exact_minimum(client):
    resp = client.patch("/scheduler/rtm-interval", json={"seconds": 10})
    assert resp.status_code == 200
    assert resp.json() == {"seconds": 10}


def test_get_anchor_interval_returns_the_default(client):
    resp = client.get("/scheduler/anchor-interval")
    assert resp.status_code == 200
    assert resp.json() == {"seconds": 900}


def test_update_anchor_interval_changes_it(client):
    resp = client.patch("/scheduler/anchor-interval", json={"seconds": 1800})
    assert resp.status_code == 200
    assert resp.json() == {"seconds": 1800}
    assert client.get("/scheduler/anchor-interval").json() == {"seconds": 1800}


def test_update_anchor_interval_accepts_exact_minimum(client):
    resp = client.patch("/scheduler/anchor-interval", json={"seconds": 300})
    assert resp.status_code == 200
    assert client.get("/scheduler/anchor-interval").json() == {"seconds": 300}


def test_update_anchor_interval_rejects_below_minimum(client):
    resp = client.patch("/scheduler/anchor-interval", json={"seconds": 299})
    assert resp.status_code == 422
    assert "300" in resp.json()["detail"]
    assert client.get("/scheduler/anchor-interval").json() == {"seconds": 900}


def test_update_anchor_interval_rejects_non_integer(client):
    assert client.patch("/scheduler/anchor-interval", json={"seconds": "soon"}).status_code == 422
    assert client.patch("/scheduler/anchor-interval", json={}).status_code == 422
