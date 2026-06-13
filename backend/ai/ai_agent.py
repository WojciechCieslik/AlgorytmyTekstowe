import ollama as ol
import time
import json
import sys
from pathlib import Path

# Dodajemy ścieżkę do bazy wektorowej, żeby importy działały poprawnie
sys.path.append(str(Path(__file__).parent.parent / "scrappers" / "vector_base"))

from recipe_embedder import RecipeEmbedder
from recipe_index import RecipeIndex
from recipe_search import RecipeSearch
from recipe_assets import load_recipes_assets_from_dir, project_main_directory
import numpy as np

from CulinaryResponse import CulinaryResponse, Crucial, NormalizedIngredients
import bases
from system_prompts import crucial_ingredients_system_prompt as sys_ing_prompt, finding_recipe_system_prompt as sys_rec_prompt, normalize_ingredients_system_prompt as sys_norm_prompt

def test_model(model_name,iterations,user_rec_prompt,sys_rec_prompt):
    message = [{'role': 'system', 'content': sys_rec_prompt},
               {'role': 'user', 'content': user_rec_prompt}]
    format = CulinaryResponse.model_json_schema()
    options = {"temperature": 0.1, "num_predict": 4096}
    # Wyłączamy wewnętrzne 'thinking' w gemma4, żeby nie zużywało limitu tokenów
    extra_kwargs = {}
    if 'gemma' in model_name:
        extra_kwargs['think'] = False

    for i in range(iterations):
        t1 = time.time()
        print(f"Iteracja {i+1}")
        response = ol.chat(
            model=model_name,
            messages=message,
            format=format,
            options=options,
            **extra_kwargs
        )
        t2 = time.time()
        content = response['message']['content']
        if not content:
            print("Pusta odpowiedź! Cała odpowiedź z Ollama:")
            print(response)
        else:
            print(content)
        print("czas: ",t2-t1)
        print("")

def add_crucial_ingredients(model_name,user_ing_prompt,sys_ing_prompt):
    message = [{'role': 'system', 'content': sys_ing_prompt},
               {'role': 'user', 'content': user_ing_prompt}]
    format = "json"
    options = {"temperature": 0.1}
    t1 = time.time()
    response = ol.chat(
        model=model_name,
        messages=message,
        format=format,
        options=options
    )
    t2 = time.time()
    #print(response['message']['content'])
    print("czas: ", t2 - t1)
    print("")
    return response['message']['content']


def normalize_ingredients(model_name, ingredients, sys_norm_prompt):
    message = [{'role': 'system', 'content': sys_norm_prompt},
               {'role': 'user', 'content': f"Znormalizuj te składniki: {ingredients}"}]
    format = NormalizedIngredients.model_json_schema()
    options = {"temperature": 0.1}
    t1 = time.time()
    response = ol.chat(
        model=model_name,
        messages=message,
        format=format,
        options=options
    )
    t2 = time.time()
    print("czas: ", t2 - t1)
    print("")
    return response['message']['content']

def get_recipe_recommendation(model_name, user_rec_prompt, sys_rec_prompt, iterations=1):
    message = [{'role': 'system', 'content': sys_rec_prompt},
               {'role': 'user', 'content': user_rec_prompt}]
    format = CulinaryResponse.model_json_schema()
    options = {"temperature": 0.1, "num_predict": 4096}
    extra_kwargs = {}
    if 'gemma' in model_name:
        extra_kwargs['think'] = False

    last_content = ""
    for i in range(iterations):
        if iterations > 1:
            print(f"Iteracja {i+1}")
        t1 = time.time()
        response = ol.chat(
            model=model_name,
            messages=message,
            format=format,
            options=options,
            **extra_kwargs
        )
        t2 = time.time()
        content = response['message']['content']
        if iterations > 1:
            print(content)
            print("czas: ", t2-t1, "\n")
        last_content = content
    return last_content

def init_db():
    print("Inicjalizacja bazy wektorowej i ładowanie modelu embeddingów (może potrwać kilka sekund)...")
    db_dir = Path(__file__).parent.parent.parent / ".lancedb"
    index = RecipeIndex(db_path=str(db_dir), table_name="recipes_ingredients_only")
    embedder = RecipeEmbedder()

    if "recipes_ingredients_only" in index.db.list_tables():
        print("Ładowanie bazy wektorowej z dysku...")
        index.tbl = index.db.open_table("recipes_ingredients_only")
    else:
        print("Baza wektorowa nie istnieje na dysku. Tworzenie i generowanie embeddingów...")
        json_dir = Path(__file__).parent.parent.parent / "json_data"
        recipes = load_recipes_assets_from_dir(json_dir)

        recipe_names = [rec['recipe_name'] for rec in recipes]
        ingredients_lists = [rec['ingredients_full'] for rec in recipes]
        vectors = embedder.embed_recipes(recipe_names, ingredients_lists)

        index.create_table(recipes, vectors)

    return RecipeSearch(embedder, index)

def run_pipeline(user_prompt: str, searcher: RecipeSearch, iterations: int = 1, recipes: int = 5) -> dict:

    qwen_norm = 'qwen3:8b'
    gemma_strong = 'gemma4:latest'

    print("Normalizacja składników...")
    normalized_ing_json = normalize_ingredients(qwen_norm, user_prompt, sys_norm_prompt)
    try:
        normalized_data = json.loads(normalized_ing_json)
        normalized_ingredients = normalized_data.get("ingredients", [user_prompt])
    except Exception as e:
        print(f"Błąd parsowania znormalizowanych składników: {e}")
        normalized_ingredients = [user_prompt]

    print(f"Znormalizowane składniki: {normalized_ingredients}")
    top_recipes = searcher.search(normalized_ingredients, k=recipes)
    
    print("\n--- Znalezione TOP przepisy ---")
    for i, r in enumerate(top_recipes, 1):
        name = r.get('recipe_name') or r.get('name', 'Nieznane')
        ingredients = r.get('ingredients_full', [])
        # Jeśli ingredients jest tablicą, złącz ją w stringa
        if isinstance(ingredients, list):
            ingredients_str = ", ".join(ingredients)
        else:
            ingredients_str = str(ingredients)
            
        print(f" {i}. {name}")
        print(f"    Składniki: {ingredients_str}")
    print("-------------------------------\n")
    
    base_subset = json.dumps(top_recipes, ensure_ascii=False, indent=2)

    user_ing_prompt = f"""
    Oto dostępne przepisy:
    {base_subset}
    Dodaj do bazy niezbędne składniki dla każdego z przepisów.
    """

    print(f"\n\n{qwen_norm}")
    print("Wyznaczanie kluczowych składników dla znalezionych przepisów...")
    crucial_ing = add_crucial_ingredients(qwen_norm, user_ing_prompt, sys_ing_prompt)
    
    print("\n--- Surowy wynik qwen3 (crucial) ---")
    print(crucial_ing)
    print("------------------------------------\n")

    try:
        crucial_dict = json.loads(crucial_ing)
        
        # Czasem qwen3 gubi główny klucz 'crucial_ingredients_for_recipes' i zwraca od razu słownik z nazwami.
        # Sprawdzamy czy istnieje ten klucz, a jeśli nie - próbujemy użyć samego słownika.
        if "crucial_ingredients_for_recipes" in crucial_dict:
            crucial_lists = crucial_dict["crucial_ingredients_for_recipes"]
        else:
            crucial_lists = crucial_dict
            
        # Słownik case-insensitive do dopasowań
        crucial_lists_lower = {k.lower(): v for k, v in crucial_lists.items()} if isinstance(crucial_lists, dict) else {}
        
        for rec in top_recipes:
            recipe_key = rec.get("name") or rec.get("recipe_name", "")
            rec["crucial"] = crucial_lists_lower.get(recipe_key.lower(), [])
            
    except Exception as e:
        print(f"Błąd parsowania crucial ingredients: {e}")
        for rec in top_recipes:
            rec["crucial"] = []

    print("\n--- Kluczowe składniki (Crucial Ingredients) ---")
    for r in top_recipes:
        name = r.get('recipe_name') or r.get('name', 'Nieznane')
        crucial = r.get('crucial', [])
        print(f" - {name}: {', '.join(crucial) if crucial else 'Brak'}")
    print("------------------------------------------------\n")

    base_subset_with_crucial = json.dumps(top_recipes, ensure_ascii=False, indent=2)

    user_rec_prompt = f"""
        Mój prompt (składniki i preferencje): {user_prompt}

        Oto pasujące przepisy, które znalazłem w mojej bazie. Każdy przepis ma teraz dodane pole 'crucial' z kluczowymi składnikami:
        ---
        {base_subset_with_crucial}
        ---
        
        Czy mogę coś z tego ugotować? Pamiętaj o BEZWZGLĘDNEJ ZASADZIE odrzucania przepisów bez kluczowych składników!
        Pod jakim linkiem znajdę przepis?
        """
    print(f"{gemma_strong}")
    print("Ocena przepisów...")
    raw_response = get_recipe_recommendation(gemma_strong, user_rec_prompt, sys_rec_prompt, iterations=iterations)
    try:
        return json.loads(raw_response)
    except Exception as e:
        print(f"Błąd parsowania ostatecznej odpowiedzi: {e}")
        print(raw_response)
        return {"info": raw_response, "found": False, "dishes": []}

if __name__ == '__main__':
    print("Testowe uruchomienie z pliku ai_agent.py...")
    sample_ingredients = "schab, ziemniaki, bułka tarta, szczypiorek, cebula, marchewka, jabłko, jajka, kurczak, kukurydza, tuńczyk, makaron, chcę coś lekkiego, może bez mięsa"
    searcher = init_db()
    result = run_pipeline(sample_ingredients, searcher=searcher, iterations=5)
    print("\n--- OSTATECZNY WYNIK (JSON) ---")
    print(json.dumps(result, indent=2, ensure_ascii=False))


