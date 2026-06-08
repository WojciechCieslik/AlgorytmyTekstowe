from backend.ai.ai_agent import add_crucial_ingredients, test_model
from vector_base.recipe_embedder import RecipeEmbedder
from vector_base.recipe_index import RecipeIndex
from vector_base.recipe_search import RecipeSearch
from ai.system_prompts import crucial_ingredients_system_prompt as sys_ing_prompt, finding_recipe_system_prompt as sys_rec_prompt

if __name__ == '__main__':
    ingredients = ["schab", "ziemniaki", "bułka tarta", "szczypiorek", "cebula", "marchewka", "jabłko", "jajka"]
    # base = json.dumps(bases.base2, ensure_ascii=False, indent=2)
    vector_db = RecipeIndex(db_path="./vector_base/vector_db")
    embedder = RecipeEmbedder()
    searcher = RecipeSearch(embedder, vector_db)

    base = searcher.search(ingredients, k=10)

    print(base)

    user_ing_prompt = f"""
    Oto dostępne przepisy:
    {base}
    Dodaj do bazy niezbędne składniki dla każdego z przepisów.
    """

    qwen_norm = 'qwen3:8b'
    qwen_light = 'qwen3:1.7b'
    gemma = 'gemma4:e2b'
    gemma_strong = 'gemma4:latest'
    iterations = 10
    models = [qwen_norm, gemma_strong]
    print(f"\n\n{qwen_norm}")

    print("crucial ingredients:")
    crucial_ing = add_crucial_ingredients(qwen_norm,user_ing_prompt,sys_ing_prompt)
    print(crucial_ing)

    user_rec_prompt = f"""
        Mam w lodówce: {ingredients}

        Oto przepisy, które znalazłem w mojej bazie oraz kluczowe dla nich składniki:
        ---
        {base}
        ---

        Oto kluczowe składniki dla każdego z przepisów:
        {crucial_ing}

        Czy mogę coś z tego ugotować?
        Pod jakim linkiem znajdę przepis?
        """
    print(f"{gemma_strong}")
    print("found_recipes:")
    test_model(gemma_strong,iterations,user_rec_prompt,sys_rec_prompt)
