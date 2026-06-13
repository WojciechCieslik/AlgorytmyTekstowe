from backend.ai.agent_gemini_api import add_crucial_ingredients, get_agent_response
from ai.system_prompts import crucial_ingredients_system_prompt as sys_ing_prompt, finding_recipe_system_prompt as sys_rec_prompt
import json
import threading

# problem z właściwą oceną składników (tortilla bez tortilli)
# halucynacja stron internetowych, z jakiegoś powodu zmienił pyszne pl na aniagotuje

vector_db = None
embedder = None
searcher = None
modele_gotowe = False

def prepare_imports():
    """Ta funkcja będzie działać w tle. Tutaj przenosimy ciężkie importy!"""
    global vector_db, embedder, searcher, modele_gotowe

    # Leniwe importy - wykonają się dopiero, gdy ten wątek wystartuje!
    from vector_base.recipe_embedder import RecipeEmbedder
    from vector_base.recipe_index import RecipeIndex
    from vector_base.recipe_search import RecipeSearch


    # Inicjalizacja ciężkich obiektów (ładowanie wag modelu do pamięci)
    vector_db = RecipeIndex(db_path="./vector_base/vector_db")
    embedder = RecipeEmbedder()
    searcher = RecipeSearch(embedder, vector_db)

    # Flaga, że wszystko jest załadowane
    modele_gotowe = True

if __name__ == '__main__':

    watek_ladowania = threading.Thread(target=prepare_imports)
    watek_ladowania.start()

    #ingredients = [x.strip() for x in input("Podaj składniki:").split(",")]

    ingredients =     [x.strip() for x in "biszkopty savoirdi,espresso, serek marscapone, kakao, wanilia, cukier, jajka".split(",")]
    print(ingredients)
    if not modele_gotowe:
        print("⏳ Analizuję przepisy, daj mi jeszcze sekundkę na rozgrzanie...")
        watek_ladowania.join()  # Blokuje program, aż watek_ladowania skończy pracę
        print("✅ Gotowe!")

    base = searcher.search(ingredients, k=20)

    user_ing_prompt = f"""
    Oto dostępne przepisy:
    {base}
    Dodaj do bazy niezbędne składniki dla każdego z przepisów.
    """
    gemini = 'gemma-4-31b-it'
    model_crucial = gemini
    model_agent = gemini
    print("crucial ingredients:")
    crucial_ing = add_crucial_ingredients(gemini,user_ing_prompt,sys_ing_prompt)
    print(crucial_ing)

    user_rec_prompt = f"""
        Mam w lodówce: {ingredients}

        Oto przepisy, które znalazłem w mojej bazie oraz kluczowe dla nich składniki:
        ---
        {base}
        ---

        Oto kluczowe składniki potrzebne do stworzenia odpowiednich przepisów:
        {crucial_ing}

        Czy mogę coś z tego ugotować?
        Pod jakim linkiem znajdę przepis?
        """

    response = get_agent_response(gemini,user_rec_prompt,sys_rec_prompt)
    try:
        response_data = json.loads(response)
        if response_data["found"]:
            print(f"Ze znalezionych składników można ugotować: {response_data["dishes"][0]["dish_name"]}\n"
                  f"Pełny przepis znajdziesz pod adresem: {response_data["dishes"][0]["dish_link"]}\n"
                  f"Dodatkowe informacje: {response_data["info"]}"
                  )

            print(f"Oto pełna lista przepisów {response_data["dishes"]}")
        else:
            print("Niestety nie udało się znaleźć odpowiedniego przepisu do podanych składników.\n"
                  f"Dodatkowe informacje: {response_data["info"]}"
                  )
    except json.JSONDecodeError:
        print("Błąd: Agent nie zwrócił poprawnego formatu JSON.")