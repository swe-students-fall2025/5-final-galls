import re
from typing import List

def normalize_ingredients(ingredients: List[str]) -> List[str]:
    normalized = []
    for ingredient in ingredients:
        # Convert to lowercase
        ingredient = ingredient.lower()
        # Remove special characters
        ingredient = re.sub(r'[^a-zA-Z0-9\s]', '', ingredient)
        # Trim whitespace
        ingredient = ingredient.strip()
        normalized.append(ingredient)
    return normalized