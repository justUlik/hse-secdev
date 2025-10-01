from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="SecDev Course App", version="0.1.0")


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    return JSONResponse(
        status_code=exc.status,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Normalize FastAPI HTTPException into our error envelope
    detail = exc.detail if isinstance(exc.detail, str) else "http_error"
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "http_error", "message": detail}},
    )


@app.get("/health")
def health():
    return {"status": "ok"}


# Example minimal entity (for tests/demo)
_DB = {"items": []}


@app.post("/items")
def create_item(name: str):
    if not name or len(name) > 100:
        raise ApiError(
            code="validation_error", message="name must be 1..100 chars", status=422
        )
    item = {"id": len(_DB["items"]) + 1, "name": name}
    _DB["items"].append(item)
    return item


@app.get("/items/{item_id}")
def get_item(item_id: int):
    for it in _DB["items"]:
        if it["id"] == item_id:
            return it
    raise ApiError(code="not_found", message="item not found", status=404)


# In-memory recipes DB
_RECIPES_DB = []


# Helper for recipe validation
def _validate_recipe(data):
    title = data.get("title", "")
    description = data.get("description", "")
    if not isinstance(title, str) or not title.strip():
        raise ApiError(
            code="validation_error", message="Title must not be empty", status=422
        )
    if not isinstance(description, str) or len(description) > 500:
        raise ApiError(
            code="validation_error",
            message="Description must be less than 500 chars",
            status=422,
        )


# 1. GET /recipes - list all recipes
@app.get("/recipes")
def list_recipes():
    return _RECIPES_DB


# 2. GET /recipes/{recipe_id} - get one recipe by id
@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int):
    for recipe in _RECIPES_DB:
        if recipe["id"] == recipe_id:
            return recipe
    raise ApiError(code="not_found", message="recipe not found", status=404)


# 3. POST /recipes - create recipe
@app.post("/recipes")
def create_recipe(recipe: dict):
    _validate_recipe(recipe)
    ingredients = recipe.get("ingredients", [])
    if not isinstance(ingredients, list):
        raise ApiError(
            code="validation_error", message="Ingredients must be a list", status=422
        )
    new_id = 1 + (_RECIPES_DB[-1]["id"] if _RECIPES_DB else 0)
    new_recipe = {
        "id": new_id,
        "title": recipe["title"],
        "description": recipe["description"],
        "ingredients": ingredients,
        "instructions": recipe.get("instructions", ""),
    }
    _RECIPES_DB.append(new_recipe)
    return new_recipe


# 4. PUT /recipes/{recipe_id} - update recipe
@app.put("/recipes/{recipe_id}")
def update_recipe(recipe_id: int, recipe: dict):
    _validate_recipe(recipe)
    ingredients = recipe.get("ingredients", [])
    if not isinstance(ingredients, list):
        raise ApiError(
            code="validation_error", message="Ingredients must be a list", status=422
        )
    for idx, r in enumerate(_RECIPES_DB):
        if r["id"] == recipe_id:
            updated = {
                "id": recipe_id,
                "title": recipe["title"],
                "description": recipe["description"],
                "ingredients": ingredients,
                "instructions": recipe.get("instructions", ""),
            }
            _RECIPES_DB[idx] = updated
            return updated
    raise ApiError(code="not_found", message="recipe not found", status=404)


# 5. DELETE /recipes/{recipe_id} - delete recipe
@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int):
    for idx, r in enumerate(_RECIPES_DB):
        if r["id"] == recipe_id:
            del _RECIPES_DB[idx]
            return {"message": "Recipe deleted"}
    raise ApiError(code="not_found", message="recipe not found", status=404)
