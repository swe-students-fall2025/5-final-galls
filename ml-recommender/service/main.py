from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

from external.spoonacular_api import get_recipes_by_ingredients
from utils.preprocessing import normalize_ingredients
# TODO: import filtering and scoring
# TODO: import caching

app = FastAPI()

class RecommendationRequest(BaseModel):
    ingredients: List[str]
    top_n: int = 5
    dietary: Optional[List[str]] = None

@app.post("/recommendations")
def recommend(request: RecommendationRequest):
    # Preprocess ingredients
    pantry = normalize_ingredients(request.ingredients)

    # TODO: caching

    # Fetch recipes from Spoonacular
    recipes = get_recipes_by_ingredients(pantry, number=request.top_n * 5)

    # TODO: Apply dietary filters

    # TODO: Score and rank recipes

    # Simplify results for the frontend
    simplified = [
        {
            "name": r["title"],
            "matched_ingredients": r.get("usedIngredientCount", 0),
            "missing_ingredients": [i["name"] for i in r.get("missedIngredients", [])],
            "image": r.get("image"),
            "dietary_tags": []  # placeholder for future filters
        }
        for r in recipes[:request.top_n]
    ]

    # Cache and return
    # TODO: caching
    return simplified