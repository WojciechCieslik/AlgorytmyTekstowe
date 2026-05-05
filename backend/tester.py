import json
import numpy as np
from recipe_parser import parse_recipe_ingredients
from recipe_embedder import RecipeEmbedder
from recipe_index import RecipeIndex
from recipe_search import RecipeSearch

def load_recipes(json_path: str) -> list:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    recipes = []
    for item in data:
        clean_names, full_texts = parse_recipe_ingredients(item['ingredients'])
        recipes.append({
            "recipe_name": item['recipe_name'],
            "url": item['url'],
            "ingredients_full": full_texts,
            "ingredients_raw": item['ingredients'],  # oryginalne pary
        })
    return recipes

def main():
    # 1. Wczytaj przepisy
    recipes = load_recipes("recipes.json")   # <-- podmień na właściwą ścieżkę

    # 2. Inicjalizacja embeddera i indeksu
    embedder = RecipeEmbedder()
    index = RecipeIndex(db_path="memory://")  # "data/lancedb" do zapisu na dysku

    # 3. Generuj embeddingi i wypełnij tabelę
    vectors = []
    for rec in recipes:
        # Do embeddingu bierzemy TYLKO nazwy (z full_texts wyciągamy same nazwy)
        # ale pełen tekst już jest w rec['ingredients_full']
        # Potrzebujemy extrakcji samych nazw jeszcze raz:
        clean_names, _ = parse_recipe_ingredients(rec['ingredients_raw'])
        vec = embedder.embed_recipe(rec['recipe_name'], clean_names)
        vectors.append(vec)

    index.create_table(recipes, np.array(vectors))

    # 4. Wyszukiwanie
    searcher = RecipeSearch(embedder, index)

    # Użytkownik podaje swoje składniki (na razie jako czyste nazwy)
    user_ingredients = ["kurczak", "cebula", "czosnek", "curry", "ryż"]
    results = searcher.search(user_ingredients, k=3)

    print("Wyniki wyszukiwania:")
    for i, res in enumerate(results):
        print(f"{i+1}. {res['name']} (podobieństwo: {res['similarity']})")
        print(f"   URL: {res['url']}")
        print(f"   Składniki: {res['ingredients_full']}\n")

if __name__ == "__main__":
    main()