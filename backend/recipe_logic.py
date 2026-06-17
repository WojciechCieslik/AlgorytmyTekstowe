import json
import threading
import sys
import os

# Zabezpieczenie przed zawieszeniem się modelu w wątku na Windowsie
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["ARROW_LOG_LEVEL"] = "FATAL"
os.environ["GLOG_minloglevel"] = "2"

# Zapewnienie, że moduły backendu będą widoczne
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'vector_base'))

from backend.ai.system_prompts import (
    crucial_ingredients_system_prompt as sys_ing_prompt,
    finding_recipe_system_prompt as sys_rec_prompt,
    normalize_ingredients_system_prompt as sys_norm_prompt,
)
from backend.ai.user_prompts import get_user_norm_prompt, get_user_rec_prompt, get_user_ing_prompt

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
    from backend.vector_base.recipe_assets import load_recipes_assets_from_dir, project_main_directory, vector_db_directory

    if status_callback:
        status_callback("Ładowanie modelu językowego i embeddera...")

    # vector_base/vector_db — ta sama lokalizacja co w main.py, ale ścieżka absolutna (GUI uruchamiane z korzenia projektu)
    db_dir = vector_db_directory
    db_dir.mkdir(parents=True, exist_ok=True)
    vector_db = RecipeIndex(db_path=str(db_dir))
    embedder = RecipeEmbedder()

    if "recipes" in vector_db.db.table_names():
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

def _parse_ingredients_fallback(ingredients_text: str) -> list[str]:
    return [part.strip() for part in ingredients_text.split(",") if part.strip()]


def _normalize_dish_link(link: str) -> str:
    link = (link or "").strip()
    if not link or link == "#":
        return ""
    if link.startswith("http://") or link.startswith("https://"):
        return link
    return f"https://{link.lstrip('/')}"


def _resolve_response_links(response: dict, base_results: list) -> dict:
    url_by_name = {res["name"].strip().lower(): res["url"] for res in base_results}

    dishes = response.get("dishes") or []
    if not dishes and response.get("dish_name"):
        dishes = [{
            "dish_name": response["dish_name"],
            "dish_link": response.get("dish_link", ""),
            "missing_ingredients": response.get("missing_ingredients", []),
        }]

    resolved_dishes = []
    for dish in dishes:
        if not isinstance(dish, dict):
            continue

        name = dish.get("dish_name", "").strip()
        link = _normalize_dish_link(dish.get("dish_link", ""))
        if not link and name:
            link = url_by_name.get(name.lower(), "")

        if not link:
            for result_name, result_url in url_by_name.items():
                if name.lower() in result_name or result_name in name.lower():
                    link = result_url
                    break

        resolved_dishes.append({
            **dish,
            "dish_name": name or dish.get("dish_name", "Nieznane danie"),
            "dish_link": link,
        })

    response["dishes"] = resolved_dishes
    if resolved_dishes and not response.get("found"):
        response["found"] = True
    return response


def _format_base_results(base_results: list, max_items: int = 10) -> str:
    lines = []
    for res in base_results[:max_items]:
        lines.append(
            f"Nazwa: {res['name']}\n"
            f"Składniki: {res.get('ingredients_full', '')}\n"
            f"Link: {res['url']}\n"
        )
    return "\n".join(lines)


def _normalize_user_ingredients(ingredients_text: str) -> list[str]:
    from backend.ai.ai_agent import normalize_ingredients

    user_norm_prompt = get_user_norm_prompt(ingredients_text)
    norm_response = normalize_ingredients('qwen3:8b', user_norm_prompt, sys_norm_prompt)
    return json.loads(norm_response)["ingredients"]


def process_ingredients(ingredients_text: str, status_callback=None, output_callback=None) -> dict:
    """
    Główna logika wyszukiwania.
    """
    if not modele_gotowe:
        init_ai_models(status_callback)

    ingredients_text = ingredients_text.strip()
    if not ingredients_text:
        return {"found": False, "info": "Proszę wpisać jakieś składniki."}

    if status_callback:
        status_callback("AI normalizuje składniki z lodówki...")

    try:
        ingredients = _normalize_user_ingredients(ingredients_text)
    except Exception:
        ingredients = _parse_ingredients_fallback(ingredients_text)

    if not ingredients:
        return {"found": False, "info": "Nie udało się rozpoznać żadnych składników."}

    if output_callback:
        output_callback("====================================")
        output_callback("ZNORMALIZOWANE SKŁADNIKI (AI):")
        output_callback(", ".join(ingredients))
        output_callback("====================================\n")

    if status_callback:
        status_callback("Wyszukiwanie przepisów w bazie wektorowej...")
        
    base_results = searcher.search(ingredients, k=10)

    base_str = _format_base_results(base_results)

    if output_callback:
        output_callback("====================================")
        output_callback("1. ZNALEZIONE PRZEPISY W BAZIE WEKTOROWEJ:")
        output_callback(base_str)
        output_callback("====================================\n")

    user_ing_prompt = get_user_ing_prompt(base_str)

    # Model konfiguracja
    model_crucial = 'qwen3:8b'
    model_agent = 'phi4:14b'

    if status_callback:
        status_callback("AI analizuje kluczowe składniki (qwen3:8b)...")

    from backend.ai.ai_agent import add_crucial_ingredients, get_agent_response

    crucial_ing = add_crucial_ingredients(model_crucial, user_ing_prompt, sys_ing_prompt)
    if not isinstance(crucial_ing, str) or not crucial_ing.strip():
        # Ollama czasem zwraca pustą odpowiedź (np. po restarcie).
        # W takim przypadku wymuś ponowną próbę, zamiast iść dalej z pustką.
        crucial_ing = add_crucial_ingredients(model_crucial, user_ing_prompt, sys_ing_prompt)

    try:
        import json
        crucial_data = json.loads(crucial_ing)
        formatted_crucial = ""
        recipes_dict = crucial_data.get("recipes", crucial_data.get("crucial_ingredients_for_recipes", crucial_data))
        if isinstance(recipes_dict, list):
            for recipe in recipes_dict:
                if isinstance(recipe, dict):
                    rec_name = recipe.get("name", "Nieznany przepis")
                    ings = recipe.get("crucial_ingredients", [])
                    if isinstance(ings, list):
                        formatted_crucial += f"{rec_name}:\n   - {', '.join(ings)}\n"
                    else:
                        formatted_crucial += f"{rec_name}:\n   - {ings}\n"
                elif isinstance(recipe, (list, tuple)):
                    # Starszy format: lista list kluczowych składników bez nazw przepisów.
                    # Zakładamy kolejność zgodną z base_results.
                    pass

            # Obsłuż listy bez nazw (np. [["schab"], ["kurczak", ...], ...])
            if not formatted_crucial and recipes_dict and all(isinstance(x, (list, tuple)) for x in recipes_dict):
                for res, ings in zip(base_results, recipes_dict):
                    formatted_crucial += f"{res['name']}:\n   - {', '.join(map(str, ings))}\n"
        elif isinstance(recipes_dict, dict):
            for rec, ings in recipes_dict.items():
                if isinstance(ings, list):
                    formatted_crucial += f"{rec}:\n   - {', '.join(ings)}\n"
                else:
                    formatted_crucial += f"{rec}:\n   - {ings}\n"
        if not formatted_crucial:
            formatted_crucial = crucial_ing
    except Exception:
        formatted_crucial = crucial_ing

    if output_callback:
        output_callback("====================================")
        output_callback("2. KLUCZOWE SKŁADNIKI WYGENEROWANE PRZEZ AI:")
        output_callback(formatted_crucial)
        output_callback("====================================\n")

    user_rec_prompt = get_user_rec_prompt(ingredients, base_str, crucial_ing)

    if status_callback:
        status_callback("Podejmowanie ostatecznej decyzji kulinarnej...")
        
    response = get_agent_response(model_agent, user_rec_prompt, sys_rec_prompt)
    
    try:
        response_data = json.loads(response)
        return _resolve_response_links(response_data, base_results)
    except json.JSONDecodeError:
        # W przypadku gdy model nie zwróci czystego JSONa, spróbujemy zignorować formatowanie i zwrócić błąd
        return {"found": False, "info": "Błąd: Agent nie zwrócił poprawnego formatu JSON. Surowa odpowiedź: " + response}
