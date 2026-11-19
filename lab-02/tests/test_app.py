from app import app
import app as app_module


def test_health_returns_ok():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "ok\n"


def test_ready_with_file_storage(monkeypatch, tmp_path):
    monkeypatch.setattr("app.DATABASE_URL", None)
    monkeypatch.setattr("app.COUNTER_FILE", tmp_path / "visits.txt")

    client = app.test_client()
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.get_json()["ready"] is True
    assert response.get_json()["store"].startswith("file:")


def test_visits_counter_increments(monkeypatch, tmp_path):
    monkeypatch.setattr("app.DATABASE_URL", None)
    monkeypatch.setattr("app.COUNTER_FILE", tmp_path / "visits.txt")

    client = app.test_client()

    first = client.get("/visits")
    second = client.get("/visits")

    assert first.status_code == 200
    assert second.status_code == 200

    assert first.get_json()["visits"] == 1
    assert second.get_json()["visits"] == 2
    assert second.get_json()["store"] == "file"


def test_visits_preserves_existing_count(monkeypatch, tmp_path):
    counter_file = tmp_path / "visits.txt"
    counter_file.write_text("10")

    monkeypatch.setattr("app.DATABASE_URL", None)
    monkeypatch.setattr("app.COUNTER_FILE", counter_file)

    client = app.test_client()
    response = client.get("/visits")

    assert response.status_code == 200
    assert response.get_json()["visits"] == 11
    assert counter_file.read_text() == "11"


def test_price_with_mocked_partner(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "sku": "MK-II",
                "price": "1234.56",
                "currency": "UAH",
            }

    def fake_get(url, timeout):
        assert url == f"{app_module.PARTNER_URL}/v1/catalog/MK-II"
        assert timeout == app_module.PARTNER_TIMEOUT
        return FakeResponse()

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    client = app.test_client()
    response = client.get("/price/MK-II")

    assert response.status_code == 200

    data = response.get_json()
    assert data["sku"] == "MK-II"
    assert data["price"] == "1234.56"
    assert data["currency"] == "UAH"


def test_price_when_partner_is_unavailable(monkeypatch):
    def fake_get(url, timeout):
        raise app_module.requests.exceptions.ConnectionError(
            "Partner service unavailable"
        )

    monkeypatch.setattr(app_module.requests, "get", fake_get)

    client = app.test_client()
    response = client.get("/price/MK-II")

    assert response.status_code == 502

    data = response.get_json()
    assert data["sku"] == "MK-II"
    assert data["error"] == "ConnectionError"
    assert "Partner service unavailable" in data["detail"]
