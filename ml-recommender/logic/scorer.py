from utils import get_ingredients

def rank_recipes(recipes, pantry_items):
    pantry_items = [item.lower().strip() for item in pantry_items]
    
    ranked = []
    for recipe in recipes:
        recipe_ingredients = get_ingredients(recipe)
        
        matched = 0
        missing = 0
        
        for ingredient in recipe_ingredients:
            if any(pantry_item in ingredient for pantry_item in pantry_items):
                matched += 1
            else:
                missing += 1
        
        total = len(recipe_ingredients)
        match_percentage = (matched / total * 100) if total > 0 else 0
        
        ranked.append({
            'recipe': recipe,
            'matched_ingredients': matched,
            'missing_ingredients': missing,
            'total_ingredients': total,
            'match_percentage': round(match_percentage, 2),
            'score': matched - (missing * 0.5)
        })
    
    ranked.sort(key=lambda x: x['score'], reverse=True)
    
    return ranked
