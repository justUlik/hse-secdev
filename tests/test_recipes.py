from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_recipes_empty():
    r = client.get("/recipes")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert len(body) == 0


def test_create_recipe_and_get():
    recipe_data = {
        "title": "Test Recipe",
        "description": "A test recipe description",
        "ingredients": ["ingredient1", "ingredient2"],
        "instructions": "Mix ingredients.",
    }
    r = client.post("/recipes", json=recipe_data)
    assert r.status_code == 200
    created = r.json()
    assert "id" in created
    recipe_id = created["id"]

    r_get = client.get(f"/recipes/{recipe_id}")
    assert r_get.status_code == 200
    fetched = r_get.json()
    assert fetched["title"] == recipe_data["title"]
    assert fetched["description"] == recipe_data["description"]
    assert fetched["ingredients"] == recipe_data["ingredients"]
    assert fetched["instructions"] == recipe_data["instructions"]


def test_create_invalid_recipe():
    invalid_data = {
        "title": "",
        "description": "Invalid recipe",
        "ingredients": ["ingredient1"],
        "instructions": "Do something.",
    }
    r = client.post("/recipes", json=invalid_data)
    assert r.status_code == 422
    body = r.json()
    assert body["error"]["code"] == "validation_error"


def test_update_recipe():
    recipe_data = {
        "title": "Original Recipe",
        "description": "Original description",
        "ingredients": ["ingredient1"],
        "instructions": "Original instructions",
    }
    r = client.post("/recipes", json=recipe_data)
    created = r.json()
    recipe_id = created["id"]

    updated_data = {
        "title": "Updated Recipe",
        "description": "Updated description",
        "ingredients": ["ingredient1", "ingredient2"],
        "instructions": "Updated instructions",
    }
    r_put = client.put(f"/recipes/{recipe_id}", json=updated_data)
    assert r_put.status_code == 200
    updated = r_put.json()
    assert updated["title"] == updated_data["title"]
    assert updated["description"] == updated_data["description"]
    assert updated["ingredients"] == updated_data["ingredients"]
    assert updated["instructions"] == updated_data["instructions"]


def test_delete_recipe():
    recipe_data = {
        "title": "Recipe to delete",
        "description": "To be deleted",
        "ingredients": ["ingredient1"],
        "instructions": "Instructions",
    }
    r = client.post("/recipes", json=recipe_data)
    created = r.json()
    recipe_id = created["id"]

    r_delete = client.delete(f"/recipes/{recipe_id}")
    assert r_delete.status_code == 200
    body = r_delete.json()
    assert body.get("message") == "Recipe deleted"

    r_get = client.get(f"/recipes/{recipe_id}")
    assert r_get.status_code == 404
    body_get = r_get.json()
    assert "error" in body_get and body_get["error"]["code"] == "not_found"
