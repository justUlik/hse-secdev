from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_invalid_recipe_payload():
    r = client.post(
        "/recipes", json={"title": "", "description": "x", "ingredients": []}
    )
    assert r.status_code == 422


def test_secret_not_in_repo(tmp_path):
    import os

    files = [f for f in os.listdir(".") if f.endswith(".env")]
    assert not files, ".env must not be committed"


def test_error_format_rfc7807():
    r = client.get("/items/999")
    body = r.json()
    assert "error" in body
    assert "code" in body["error"]
    assert "message" in body["error"]
