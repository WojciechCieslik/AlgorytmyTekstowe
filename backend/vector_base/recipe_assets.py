from pathlib import Path
from recipe_parser import parse_recipe_ingredients
import json

project_main_directory = Path(__file__).resolve().parent.parent.parent
backend_directory = Path(__file__).resolve().parent.parent
VECTOR_DB_RELATIVE = "vector_base/vector_db"
vector_db_directory = backend_directory / "vector_base" / "vector_db"

# Load every file from a given 'dir_path' what satisfies format '*.json'
def load_recipes_assets_from_dir(dir_path: Path) -> list:
    all_recipes = []
    base_path = dir_path

    if not base_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    for json_file in base_path.glob("*.json"):
        print(f"Loading data from [{json_file}]")
        recipes = load_recipes(str(json_file))
        all_recipes.extend(recipes)

    return all_recipes

# Load recipes from single file
def load_recipes(json_path: str) -> list:
    recipes = []

    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        if not content:
            return recipes

        try:
            items = json.loads(content)
            if not isinstance(items, list):
                items = [items]
        except json.JSONDecodeError:
            items = []
            for line in content.splitlines():
                if line.strip():
                    try:
                        items.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

        for item in items:
            recipe_name = item.get('recipe_name') or item.get('name') or 'unknown'
            full_texts = parse_recipe_ingredients(item['ingredients'])

            recipes.append({
                "recipe_name": recipe_name,
                "url": item['url'],
                "ingredients_full": full_texts,
            })

    return recipes
