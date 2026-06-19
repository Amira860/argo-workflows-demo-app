def test_index_returns_metadata(app_client):
    response = app_client.get("/")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["app"] == "argo-workflows-demo-app"
    assert payload["environment"] == "dev"
    assert payload["version"] == "0.1.0"


def test_search_filters_catalog(app_client):
    response = app_client.get("/api/search?q=front")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["count"] == 1
    assert payload["items"][0]["name"] == "ui-portal"
