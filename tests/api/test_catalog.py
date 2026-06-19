import requests


def test_catalog_returns_items(live_server_url):
    response = requests.get(f"{live_server_url}/api/catalog", timeout=5)

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] >= 4
    assert any(item["name"] == "workflow-engine" for item in payload["items"])


def test_search_endpoint_supports_query(live_server_url):
    response = requests.get(f"{live_server_url}/api/search", params={"q": "backend"}, timeout=5)

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 2
