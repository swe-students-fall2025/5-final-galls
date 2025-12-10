from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from service.external.spoonacular_api import get_recipes_by_ingredients
from utils.preprocessing import normalize_ingredients
from logic.filters import validate_restrictions, filter_recipes
from logic.filters import validate_restrictions
from logic.scorer import rank_recipes
from logic.ingredients import get_ingredients

# TODO: import caching

app = FastAPI()

origins = [
    "http://localhost:5001",
    "http://127.0.0.1:5001",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendationRequest(BaseModel):
    ingredients: List[str]
    top_n: int = 5
    dietary: Optional[List[str]] = None
    intolerances: Optional[List[str]] = None
    excluded_ingredients: Optional[List[str]] = None

@app.post("/recommendations")
def recommend(request: RecommendationRequest):
    # Preprocess ingredients
    pantry = normalize_ingredients(request.ingredients)

    # TODO: caching

    # Fetch recipes from Spoonacular
    recipes = get_recipes_by_ingredients(pantry, request.top_n * 5, request.dietary)

    restrictions = validate_restrictions({
        "diet": request.dietary,
        "intolerances": request.intolerances,
        "excluded_ingredients": request.excluded_ingredients
    })

    filtered_recipes = filter_recipes(recipes, restrictions)

    ranked_recipes = rank_recipes(filtered_recipes, pantry)

    # Simplify results for the frontend
    simplified = []
    for r in recipes:
        used = [i["name"] for i in r.get("usedIngredients") or []]
        missed = [i["name"] for i in r.get("missedIngredients") or []]

        simplified.append({
            "id": r.get("id"),
            "name": r.get("title"),
            "matched_ingredients": used,
            "missing_ingredients": missed,
            "image": r.get("image"),
            "dietary_tags": r.get("diets", [])
        })

    # Cache and return
    # TODO: caching
    return simplified