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
    #index = RecipeIndex(db_path="memory://")
    index = RecipeIndex(db_path="./vector_db")

    # 3. Generuj embeddingi i wypełnij tabelę
    vectors = []
    prawdziwe_przepisy = []  # Tworzymy nową listę tylko na poprawne dane

    for rec in recipes:
        clean_names, _ = parse_recipe_ingredients(rec['ingredients_raw'])

        # FILTR: Jeśli po oczyszczeniu przepis nie ma składników (to artykuł, nie przepis)
        # to po prostu go ignorujemy i idziemy dalej!
        if not clean_names:
            continue

        vec = embedder.embed_recipe(rec['recipe_name'], clean_names)
        vectors.append(vec)
        prawdziwe_przepisy.append(rec)  # Dodajemy tylko te, które przetrwały

    # Tworzymy bazę TYLKO z prawdziwych przepisów
    index.create_table(prawdziwe_przepisy, np.array(vectors))

    # 4. Wyszukiwanie
    searcher = RecipeSearch(embedder, index)

    # Użytkownik podaje swoje składniki (na razie jako czyste nazwy)
    user_ingredients = ["kurczak", "cebula", "czosnek", "curry", "ryż"]
    results = searcher.search(user_ingredients, k=10)

    print("Wyniki wyszukiwania:")
    for i, res in enumerate(results):
        print(f"{i+1}. {res['name']} (podobieństwo: {res['similarity']})")
        print(f"   URL: {res['url']}")
        print(f"   Składniki: {res['ingredients_full']}\n")

if __name__ == "__main__":
    main()
