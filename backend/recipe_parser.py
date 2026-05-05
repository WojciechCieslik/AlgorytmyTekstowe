from typing import List, Tuple

def parse_recipe_ingredients(ingredients: List[List[str]]) -> Tuple[List[str], List[str]]:
    clean_names = []
    full_texts = []

    for pair in ingredients:
        name = pair[0].strip()
        unit = pair[1].strip() if len(pair) > 1 else ''

        sub_names = [n.strip() for n in name.split(',') if n.strip()]
        for sub in sub_names:
            clean_names.append(sub)
            full_texts.append(f"{unit} {sub}".strip())

    seen = set()
    unique_clean = []
    for n in clean_names:
        if n not in seen:
            seen.add(n)
            unique_clean.append(n)

    return unique_clean, full_texts