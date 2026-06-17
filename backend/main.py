from backend.ai.ai_agent import add_crucial_ingredients, get_agent_response,normalize_ingredients
from ai.system_prompts import crucial_ingredients_system_prompt as sys_ing_prompt, finding_recipe_system_prompt as sys_rec_prompt, normalize_ingredients_system_prompt as sys_norm_prompt
from ai.user_prompts import  get_user_norm_prompt,get_user_rec_prompt,get_user_ing_prompt
import json
import threading


vector_db = None
embedder = None
searcher = None
modele_gotowe = False

def prepare_imports():
    global vector_db, embedder, searcher, modele_gotowe

    # Leniwe importy
    from vector_base.recipe_embedder import RecipeEmbedder
    from vector_base.recipe_index import RecipeIndex
    from vector_base.recipe_search import RecipeSearch


    # Inicjalizacja bazy (vector_base/vector_db względem katalogu backend/)
    vector_db = RecipeIndex(db_path="vector_base/vector_db")
    embedder = RecipeEmbedder()
    searcher = RecipeSearch(embedder, vector_db)
    modele_gotowe = True

if __name__ == '__main__':
    qwen_norm = 'qwen3:8b'
    phi = 'phi4:14b'
    watek_ladowania = threading.Thread(target=prepare_imports)
    watek_ladowania.start()
    while True:


        #user_ingredients = input("Podaj składniki:")
        user_ingredients =     "mąka, cukier, mleko, jajka, kakao, czekolada gorzka, czekolada mleczna, cynamon, soda oczyszczona,masło, proszek do pieczenia, sól, cytryna, wiśnie"

        user_norm_prompt = get_user_norm_prompt(user_ingredients)
        ingredients = json.loads(normalize_ingredients(qwen_norm,sys_norm_prompt,user_norm_prompt))["ingredients"]
        print(ingredients)
        if not modele_gotowe:
            print("⏳ Analizuję przepisy, daj mi jeszcze sekundkę na rozgrzanie...")
            watek_ladowania.join()  # Blokuje program, aż watek_ladowania skończy pracę
            print("✅ Gotowe!")


        base = searcher.search(ingredients, k=10)
        print(base)

        user_ing_prompt = get_user_ing_prompt(base)
        print("crucial ingredients:")
        crucial_ing = add_crucial_ingredients(qwen_norm,user_ing_prompt,sys_ing_prompt)
        print(crucial_ing)

        user_rec_prompt = get_user_rec_prompt(ingredients, base, crucial_ing)
        response = get_agent_response(phi,user_rec_prompt,sys_rec_prompt)
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