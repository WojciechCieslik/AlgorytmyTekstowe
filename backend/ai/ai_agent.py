import ollama as ol
import time
#import ragas
from CulinaryResponse import CulinaryResponse,Crucial
import json
import bases
from system_prompts import crucial_ingredients_system_prompt as sys_ing_prompt, finding_recipe_system_prompt as sys_rec_prompt


def test_model(model_name,iterations,user_rec_prompt,sys_rec_prompt):
    message = [{'role': 'system', 'content': sys_rec_prompt},
               {'role': 'user', 'content': user_rec_prompt}]
    format = CulinaryResponse.model_json_schema()
    options = {"temperature": 1}

    for i in range(iterations):
        t1 = time.time()
        print(f"Iteracja {i+1}")
        response = ol.chat(
            model=model_name,
            messages=message,
            format=format,
            options=options
        )
        t2 = time.time()
        print(response['message']['content'])
        print("czas: ",t2-t1)
        print("")

def add_crucial_ingredients(model_name,user_ing_prompt,sys_ing_prompt):
    message = [{'role': 'system', 'content': sys_ing_prompt},
               {'role': 'user', 'content': user_ing_prompt}]
    format = Crucial.model_json_schema()
    options = {"temperature":1}
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


if __name__ == '__main__':
    print("działa1")
    ingredients = ["schab","ziemniaki","bułka tarta","szczypiorek","cebula","marchewka", "jabłko","jajka","kurczak"]
    base = json.dumps(bases.base2, ensure_ascii=False, indent=2)

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
    models = [qwen_norm,gemma_strong]
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

