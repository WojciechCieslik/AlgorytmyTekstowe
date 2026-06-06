import json
import numpy as np
from recipe_embedder import RecipeEmbedder
from recipe_index import RecipeIndex
from recipe_search import RecipeSearch
from recipe_assets import load_recipes_assets_from_dir, project_main_directory,parse_recipe_ingredients

def main():
    json_dir = project_main_directory / "json_data"
    recipes = load_recipes_assets_from_dir(json_dir)

    embedder = RecipeEmbedder()
    index = RecipeIndex(db_path="memory://")

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
