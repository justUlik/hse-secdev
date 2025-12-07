from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_logging_no_pii(tmp_path, monkeypatch):
    log_file = tmp_path / "app.log"
    monkeypatch.setenv("APP_LOG_DIR", str(tmp_path))

    from importlib import reload

    import app.main as main

    reload(main)

    client = TestClient(main.app)

    payload = {
        "title": "Secret Dish",
        "description": "Very private",
        "ingredients": ["password123", "token456"],
        "instructions": "Mix confidentially",
    }

    client.post("/recipes", json=payload)

    content = log_file.read_text()

    assert "password123" not in content
    assert "token456" not in content
    assert "confidential" not in content

    assert "request" in content or "api_error" in content
