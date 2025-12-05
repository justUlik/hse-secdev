from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from app.database import Base, engine, SessionLocal
from app.models import Recipe
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
def list_recipes(db: Session = Depends(get_db)):
    recipes = db.query(Recipe).all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "ingredients": r.ingredients.split("||"),
            "instructions": r.instructions,
        }
        for r in recipes
    ]


# 2. GET /recipes/{recipe_id} - get one recipe by id
@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise ApiError(code="not_found", message="recipe not found", status=404)

    return {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "ingredients": recipe.ingredients.split("||"),
        "instructions": recipe.instructions or "",
    }


# 3. POST /recipes - create recipe
@app.post("/recipes")
def create_recipe(recipe: dict, db: Session = Depends(get_db)):
    _validate_recipe(recipe)

    ingredients = recipe.get("ingredients", [])
    if not isinstance(ingredients, list):
        raise ApiError(
            code="validation_error",
            message="Ingredients must be a list",
            status=422,
        )

    db_recipe = Recipe(
        title=recipe["title"],
        description=recipe["description"],
        ingredients="||".join(ingredients),
        instructions=recipe.get("instructions", "") or "",
    )
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)

    return {
        "id": db_recipe.id,
        "title": db_recipe.title,
        "description": db_recipe.description,
        "ingredients": ingredients,
        "instructions": db_recipe.instructions,
    }


# 4. PUT /recipes/{recipe_id} - update recipe
@app.put("/recipes/{recipe_id}")
def update_recipe(recipe_id: int, recipe: dict, db: Session = Depends(get_db)):
    _validate_recipe(recipe)

    ingredients = recipe.get("ingredients", [])
    if not isinstance(ingredients, list):
        raise ApiError(
            code="validation_error",
            message="Ingredients must be a list",
            status=422,
        )

    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not db_recipe:
        raise ApiError(code="not_found", message="recipe not found", status=404)

    db_recipe.title = recipe["title"]
    db_recipe.description = recipe["description"]
    db_recipe.ingredients = "||".join(ingredients)
    db_recipe.instructions = recipe.get("instructions", "") or ""

    db.commit()
    db.refresh(db_recipe)

    return {
        "id": db_recipe.id,
        "title": db_recipe.title,
        "description": db_recipe.description,
        "ingredients": ingredients,
        "instructions": db_recipe.instructions,
    }


# 5. DELETE /recipes/{recipe_id} - delete recipe
@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not db_recipe:
        raise ApiError(code="not_found", message="recipe not found", status=404)

    db.delete(db_recipe)
    db.commit()

    return {"message": "Recipe deleted"}
