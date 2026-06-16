import json
import threading
import sys
import os

# Zabezpieczenie przed zawieszeniem się modelu w wątku na Windowsie
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Zapewnienie, że moduły backendu będą widoczne
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'vector_base'))

from backend.ai.ai_agent import get_agent_response, add_crucial_ingredients
from backend.ai.system_prompts import crucial_ingredients_system_prompt as sys_rec_prompt, \
    finding_recipe_system_prompt as sys_ing_prompt

# Zmienne globalne na nasze ciężkie modele
vector_db = None
embedder = None
searcher = None
modele_gotowe = False

def init_ai_models(status_callback=None):
    """
    Funkcja ładująca modele. Weryfikuje również czy istnieje baza.
    Może przyjąć funkcję callback do odświeżania statusu w UI.
    """
    global vector_db, embedder, searcher, modele_gotowe
    
    if modele_gotowe:
        return

    from backend.vector_base.recipe_embedder import RecipeEmbedder
    from backend.vector_base.recipe_index import RecipeIndex
    from backend.vector_base.recipe_search import RecipeSearch
    
    # Importy potrzebne do generowania bazy
    from backend.vector_base.recipe_assets import load_recipes_assets_from_dir, project_main_directory

    if status_callback:
        status_callback("Ładowanie modelu językowego i embeddera...")

    # Ścieżka do bazy
    db_dir = project_main_directory / "./backend/vector_base/vector_db"
    vector_db = RecipeIndex(db_path=str(db_dir))
    embedder = RecipeEmbedder()

    if "recipes" in vector_db.db.list_tables():
        if status_callback:
            status_callback("Baza wektorowa znaleziona. Ładowanie...")
        vector_db.tbl = vector_db.db.open_table("recipes")
    else:
        if status_callback:
            status_callback("Pierwsze uruchomienie. Trwa tworzenie i wektoryzacja bazy przepisów (może to zająć chwilę)...")
        json_dir = project_main_directory / "json_data"
        recipes = load_recipes_assets_from_dir(json_dir)

        recipe_names = [rec['recipe_name'] for rec in recipes]
        ingredients_lists = [rec['ingredients_full'] for rec in recipes]
        vectors = embedder.embed_recipes(recipe_names, ingredients_lists)

        vector_db.create_table(recipes, vectors)

    if status_callback:
        status_callback("Inicjalizacja wyszukiwarki...")
        
    searcher = RecipeSearch(embedder, vector_db)
    modele_gotowe = True
    
    if status_callback:
        status_callback("Gotowe!")

def start_background_init(status_callback=None):
    """Uruchamia ładowanie w osobnym wątku."""
    if not modele_gotowe:
        watek = threading.Thread(target=init_ai_models, args=(status_callback,))
        watek.start()
        return watek
    return None

def process_ingredients(ingredients: list[str], status_callback=None, output_callback=None) -> dict:
    """
    Główna logika wyszukiwania.
    """
    if not modele_gotowe:
        init_ai_models(status_callback)

    if status_callback:
        status_callback("Wyszukiwanie przepisów w bazie wektorowej...")
        
    base_results = searcher.search(ingredients, k=10)
    
    # Format the results into string format for prompt context
    base = []
    for i, res in enumerate(base_results):
        # We need to construct a representation
        base.append(f"Nazwa: {res['name']}\nSkładniki: {res['ingredients_full']}\nLink: {res['url']}\n")
    base_str = "\n".join(base)

    if output_callback:
        output_callback("====================================")
        output_callback("🔎 1. ZNALEZIONE PRZEPISY W BAZIE WEKTOROWEJ:")
        output_callback(base_str)
        output_callback("====================================\n")

    user_ing_prompt = f"""
        Oto dostępne przepisy:
        {base_str}
        Dodaj do bazy niezbędne składniki dla każdego z przepisów.
        """

    # Model konfiguracja
    model_crucial = 'qwen3:8b'
    model_agent = 'phi4:14b'

    if status_callback:
        status_callback("AI analizuje kluczowe składniki do przepisów...")
        
    crucial_ing = add_crucial_ingredients(model_crucial, user_ing_prompt, sys_ing_prompt)

    try:
        import json
        crucial_data = json.loads(crucial_ing)
        formatted_crucial = ""
        recipes_dict = crucial_data.get("crucial_ingredients_for_recipes", crucial_data)
        if isinstance(recipes_dict, dict):
            for rec, ings in recipes_dict.items():
                if isinstance(ings, list):
                    formatted_crucial += f"📌 {rec}:\n   - {', '.join(ings)}\n"
                else:
                    formatted_crucial += f"📌 {rec}:\n   - {ings}\n"
        if not formatted_crucial:
            formatted_crucial = crucial_ing
    except Exception:
        formatted_crucial = crucial_ing

    if output_callback:
        output_callback("====================================")
        output_callback("🧠 2. KLUCZOWE SKŁADNIKI WYGENEROWANE PRZEZ AI:")
        output_callback(formatted_crucial)
        output_callback("====================================\n")

    user_rec_prompt = f"""
            Mam w lodówce: {ingredients}

            Oto przepisy, które znalazłem w mojej bazie oraz kluczowe dla nich składniki:
            ---
            {base_str}
            ---

            Oto kluczowe składniki potrzebne do stworzenia odpowiednich przepisów:
            {crucial_ing}

            Czy mogę coś z tego ugotować?
            Pod jakim linkiem znajdę przepis?
            """

    if status_callback:
        status_callback("Podejmowanie ostatecznej decyzji kulinarnej...")
        
    response = get_agent_response(model_agent, user_rec_prompt, sys_rec_prompt)
    
    try:
        response_data = json.loads(response)
        return response_data
    except json.JSONDecodeError:
        # W przypadku gdy model nie zwróci czystego JSONa, spróbujemy zignorować formatowanie i zwrócić błąd
        return {"found": False, "info": "Błąd: Agent nie zwrócił poprawnego formatu JSON. Surowa odpowiedź: " + response}
