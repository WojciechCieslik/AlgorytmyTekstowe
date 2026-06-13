from backend.ai.ai_agent import add_crucial_ingredients, test_model, get_agent_response
from vector_base.recipe_embedder import RecipeEmbedder
from vector_base.recipe_index import RecipeIndex
from vector_base.recipe_search import RecipeSearch
from ai.system_prompts import crucial_ingredients_system_prompt as sys_ing_prompt, finding_recipe_system_prompt as sys_rec_prompt
import json

# problem z właściwą oceną składników (tortilla bez tortilli)
# halucynacja stron internetowych, z jakiegoś powodu zmienił pyszne pl na aniagotuje



if __name__ == '__main__':

    #ingredients = [x.strip() for x in input("Podaj składniki:").split(",")]

    ingredients =     [x.strip() for x in "passata, wołowina, jajko, mleko, papryka, pomidory, kukurydza, fasola, ryż, chili, cukier, sól, papryka wędzona, cebula,kurczak,tortilla,marchewka, czosnek, mąka".split(",")]
    print(ingredients)
    vector_db = RecipeIndex(db_path="./vector_base/vector_db")
    embedder = RecipeEmbedder()
    searcher = RecipeSearch(embedder, vector_db)

    base = searcher.search(ingredients, k=10)

    user_ing_prompt = f"""
    Oto dostępne przepisy:
    {base}
    Dodaj do bazy niezbędne składniki dla każdego z przepisów.
    """

    qwen_norm = 'qwen3:8b'
    qwen_strong = 'qwen3:14b'
    gemma = 'gemma4:latest'
    gemma_strong = 'gemma4:12b'
    phi = 'phi4:14b'
    models = [qwen_norm,qwen_strong ,phi]

    print("crucial ingredients:")
    crucial_ing = add_crucial_ingredients(qwen_norm,user_ing_prompt,sys_ing_prompt)
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
    # print(f"{gemma}")
    #for agent in models:
    #print(f"{agent}")
    response = get_agent_response(phi,user_rec_prompt,sys_rec_prompt)
    try:
        response_data = json.loads(response)
        if response_data["found"]:
            print(f"Ze znalezionych składników można ugotować: {response_data["dish_name"]}\n"
                  f"Pełny przepis znajdziesz pod adresem: {response_data["dish_link"]}\n"
                  f"Dodatkowe informacje: {response_data["info"]}"
                  )
        else:
            print("Niestety nie udało się znaleźć odpowiedniego przepisu do podanych składników.\n"
                  f"Dodatkowe informacje: {response_data["info"]}"
                  )
    except json.JSONDecodeError:
        print("Błąd: Agent nie zwrócił poprawnego formatu JSON.")
