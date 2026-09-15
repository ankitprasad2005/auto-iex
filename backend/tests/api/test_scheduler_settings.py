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
