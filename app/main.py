import logging
import os
from typing import Any, Dict, List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import Recipe

Base.metadata.create_all(bind=engine)


# --------------------- DB Session ---------------------


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------------- FastAPI app ----------------------


app = FastAPI(title="SecDev Course App", version="0.1.0")

# --------------------- Logs ----------------------


LOG_DIR = os.getenv("APP_LOG_DIR", "/app/logs")
os.makedirs(LOG_DIR, exist_ok=True)

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "app.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger("secdev")

# --------------------- ERROR HANDLING ----------------------


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    logger.warning(f"API error: code={exc.code} path={request.url.path}")
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


# --------------------- SECURITY HEADERS (S06-06) ----------------------


@app.middleware("http")
async def log_and_secure(request: Request, call_next):
    try:
        response = await call_next(request)
    except ApiError as exc:
        logger.warning(f"API error: code={exc.code} path={request.url.path}")
        response = JSONResponse(
            status_code=exc.status,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    logger.info(
        f"request method={request.method} path={request.url.path} status={response.status_code}"
    )

    return response


# --------------------- DEMO /items API (как было) ----------------------


_DB: Dict[str, List[Dict[str, Any]]] = {"items": []}


@app.post("/items")
def create_item(name: str):
    if not name or len(name) > 100:
        raise ApiError(code="validation_error", message="name must be 1..100 chars", status=422)
    item = {"id": len(_DB["items"]) + 1, "name": name}
    _DB["items"].append(item)
    return item


@app.get("/items/{item_id}")
def get_item(item_id: int):
    for it in _DB["items"]:
        if it["id"] == item_id:
            return it
    raise ApiError(code="not_found", message="item not found", status=404)


# --------------------- STRONG VALIDATION FOR RECIPES (S06-04) ----------------------


def _validate_recipe(data: dict):
    title = data.get("title")
    description = data.get("description")
    ingredients = data.get("ingredients")
    instructions = data.get("instructions", "")

    # title: 1..120
    if not isinstance(title, str) or not (1 <= len(title) <= 120):
        raise ApiError("validation_error", "Invalid title length", 422)

    # description: 1..2000
    if not isinstance(description, str) or not (1 <= len(description) <= 2000):
        raise ApiError("validation_error", "Invalid description length", 422)

    # ingredients: non-empty list of short strings
    if not isinstance(ingredients, list) or len(ingredients) == 0:
        raise ApiError("validation_error", "Ingredients must be a non-empty list", 422)

    for entry in ingredients:
        if not isinstance(entry, str) or not (1 <= len(entry) <= 200):
            raise ApiError("validation_error", "Invalid ingredient entry", 422)

    # instructions: optional, ≤ 5000 chars
    if not isinstance(instructions, str) or len(instructions) > 5000:
        raise ApiError("validation_error", "Instructions too long", 422)


# --------------------- RECIPES CRUD (через SQLAlchemy) ----------------------


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


@app.post("/recipes")
def create_recipe(recipe: dict, db: Session = Depends(get_db)):
    _validate_recipe(recipe)

    db_recipe = Recipe(
        title=recipe["title"],
        description=recipe["description"],
        ingredients="||".join(recipe["ingredients"]),
        instructions=recipe.get("instructions", "") or "",
    )
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)

    return {
        "id": db_recipe.id,
        "title": db_recipe.title,
        "description": db_recipe.description,
        "ingredients": recipe["ingredients"],
        "instructions": db_recipe.instructions,
    }


@app.put("/recipes/{recipe_id}")
def update_recipe(recipe_id: int, recipe: dict, db: Session = Depends(get_db)):
    _validate_recipe(recipe)

    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not db_recipe:
        raise ApiError(code="not_found", message="recipe not found", status=404)

    db_recipe.title = recipe["title"]
    db_recipe.description = recipe["description"]
    db_recipe.ingredients = "||".join(recipe["ingredients"])  # type: ignore[assignment]
    db_recipe.instructions = recipe.get("instructions", "") or ""  # type: ignore[assignment]

    db.commit()
    db.refresh(db_recipe)

    return {
        "id": db_recipe.id,
        "title": db_recipe.title,
        "description": db_recipe.description,
        "ingredients": recipe["ingredients"],
        "instructions": db_recipe.instructions,
    }


@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not db_recipe:
        raise ApiError(code="not_found", message="recipe not found", status=404)

    db.delete(db_recipe)
    db.commit()

    return {"message": "Recipe deleted"}
