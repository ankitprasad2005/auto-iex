def test_cors_allows_cross_origin_requests(client):
    resp = client.get("/chain", headers={"Origin": "http://localhost:5173"})
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "*"


def test_cors_preflight_allows_post_with_json_headers(client):
    resp = client.options(
        "/scenarios",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "*"
    assert "POST" in resp.headers.get("access-control-allow-methods", "")
