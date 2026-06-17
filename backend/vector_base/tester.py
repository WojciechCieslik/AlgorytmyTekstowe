import json
import numpy as np
from recipe_embedder import RecipeEmbedder
from recipe_index import RecipeIndex
from recipe_search import RecipeSearch
from recipe_assets import load_recipes_assets_from_dir, project_main_directory

def main():
    db_dir = project_main_directory / "backend/vector_base/vector_db"
    index = RecipeIndex(db_path=str(db_dir))
    embedder = RecipeEmbedder()

    if "recipes" in index.db.table_names():
        print("Tabela 'recipes' już istnieje. Ładowanie z dysku...")
        index.tbl = index.db.open_table("recipes")
    else:
        print("Baza wektorowa nie istnieje na dysku. Tworzenie i generowanie embeddingów...")
        json_dir = project_main_directory / "json_data"
        recipes = load_recipes_assets_from_dir(json_dir)

        # Używamy zoptymalizowanego batchowania
        recipe_names = [rec['recipe_name'] for rec in recipes]
        ingredients_lists = [rec['ingredients_full'] for rec in recipes]
        vectors = embedder.embed_recipes(recipe_names, ingredients_lists)

        index.create_table(recipes, vectors)

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
