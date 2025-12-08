from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_security_headers():
    resp = client.get("/health")
    h = resp.headers
    assert h.get("X-Content-Type-Options") == "nosniff"
    assert h.get("X-Frame-Options") == "DENY"
    assert h.get("Referrer-Policy") == "no-referrer"
    assert "default-src 'self'" in (h.get("Content-Security-Policy") or "")


def test_validate_title_too_long():
    r = client.post(
        "/recipes",
        json={"title": "a" * 300, "description": "ok", "ingredients": ["salt"], "instructions": ""},
    )
    assert r.status_code == 422


def test_validate_ingredients_not_list():
    r = client.post(
        "/recipes",
        json={"title": "ok", "description": "ok", "ingredients": "not-a-list", "instructions": ""},
    )
    assert r.status_code == 422


def test_validate_ingredient_entry_too_long():
    r = client.post(
        "/recipes",
        json={"title": "ok", "description": "ok", "ingredients": ["a" * 500], "instructions": ""},
    )
    assert r.status_code == 422
