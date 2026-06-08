from typing import List, Tuple, Any


def parse_recipe_ingredients(ingredients: List[Any]) -> Tuple[List[str], List[str]]:
    clean_names = []
    full_texts = []

    for item in ingredients:
        name = ""
        unit = ""

        if isinstance(item, list) and len(item) > 0:
            if item[0] is None:
                continue
            name = str(item[0]).strip()
            unit = str(item[1]).strip() if len(item) > 1 and item[1] is not None else ''

        elif isinstance(item, str):
            name = item.strip()
            unit = ''

        else:
            continue

        if not name:
            continue

        sub_names = [n.strip() for n in name.split(',') if n.strip()]
        for sub in sub_names:
            clean_names.append(sub)
            tekst = f"{unit} {sub}".strip() if unit else sub
            full_texts.append(tekst)

    # Wypisujemy na konsolę wynik dla podglądu (Tryb Detektywa)
    if not full_texts:
        print(f"⚠️ UWAGA! Parser zwrócił pustą listę dla wejścia: {ingredients}")

    seen = set()
    unique_clean = []
    for n in clean_names:
        if n not in seen:
            seen.add(n)
            unique_clean.append(n)

    return unique_clean, full_texts