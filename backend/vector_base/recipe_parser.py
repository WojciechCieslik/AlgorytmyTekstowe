from typing import List, Union

def parse_recipe_ingredients(ingredients: List[Union[str, List[str]]]) -> List[str]:
    full_texts = []

    for item in ingredients:
        if isinstance(item, (list, tuple)):
            # sklejaj gdy ilość i nazwa są oddzielnie
            parts = [str(p).strip() for p in item if p is not None and str(p).strip()]
            if len(parts) == 2:
                full_text = f"{parts[1]} {parts[0]}".strip()
            else:
                full_text = " ".join(parts)
        else:
            # w przeciwnym wypadku nie tykaj
            full_text = str(item).strip()

        if full_text:
            full_texts.append(full_text)

    seen = set()
    unique_clean = []
    for n in full_texts:
        if n not in seen:
            seen.add(n)
            unique_clean.append(n)

    return unique_clean

