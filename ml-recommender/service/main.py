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

import requests
import os

API_KEY = os.getenv("SPOONACULAR_API_KEY","1630fb1bb80c4451896924049cf16ebf")
BASE_URL = "https://api.spoonacular.com"

def get_recipe_instructions(recipe_id: int):
    """Fetch step-by-step instructions for a recipe from Spoonacular"""
    url = f"{BASE_URL}/recipes/{recipe_id}/analyzedInstructions"
    params = {"apiKey": API_KEY, "stepBreakdown": True}

    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        formatted = []
        for section in data:
            formatted_section = {
                "name": section.get("name", "Main Recipe"),
                "steps": []
            }
            for step in section.get("steps", []):
                formatted_section["steps"].append({
                    "number": step.get("number"),
                    "instruction": step.get("step"),
                    "ingredients": [i["name"] for i in step.get("ingredients", [])],
                    "equipment": [e["name"] for e in step.get("equipment", [])],
                    "time": step.get("length")
                })
            formatted.append(formatted_section)
        return formatted
    except Exception as e:
        print(f"Error fetching instructions for recipe {recipe_id}: {e}")
        return []

@app.post("/recommendations")
def recommend(request: RecommendationRequest):
    # Preprocess ingredients
    pantry = normalize_ingredients(request.ingredients)
    print(1)
    print(2)
    # Fetch recipes from Spoonacular
    recipes = get_recipes_by_ingredients(pantry, request.top_n * 5, request.dietary)
    print(3)
    restrictions = validate_restrictions({
        "diet": request.dietary,
        "intolerances": request.intolerances,
        "excluded_ingredients": request.excluded_ingredients
    })
    print(4)
    filtered_recipes = filter_recipes(recipes, restrictions)
    print(5)
    ranked_recipes = rank_recipes(filtered_recipes, pantry)
    print(6)
    # Simplify results for the frontend
    simplified = []
    for r in recipes:
        used = [i["name"] for i in r.get("usedIngredients") or []]
        missed = [i["name"] for i in r.get("missedIngredients") or []]

        instructions = get_recipe_instructions(r.get("id"))

        simplified.append({
            "id": r.get("id"),
            "name": r.get("title"),
            "matched_ingredients": used,
            "missing_ingredients": missed,
            "image": r.get("image"),
            "dietary_tags": r.get("diets", []),
            "instructions": instructions
        })
    print(7)
    # Cache and return
    # TODO: caching
    return simplified

