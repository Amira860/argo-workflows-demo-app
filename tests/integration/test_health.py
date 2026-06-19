import requests


def test_health_endpoint_is_ok(live_server_url):
    response = requests.get(f"{live_server_url}/health", timeout=5)

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["environment"] == "dev"
