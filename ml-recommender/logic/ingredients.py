def get_ingredients(recipe):
    ingredients = []
    
    if 'extendedIngredients' in recipe:
        for ing in recipe['extendedIngredients']:
            name = ing.get('name') or ing.get('originalName') or ing.get('original', '')
            if name:
                ingredients.append(name.lower())
    
    elif 'ingredients' in recipe:
        for ing in recipe['ingredients']:
            if isinstance(ing, str):
                ingredients.append(ing.lower())
            elif isinstance(ing, dict):
                name = ing.get('name') or ing.get('originalName') or ing.get('original', '')
                if name:
                    ingredients.append(name.lower())
    
    return ingredients