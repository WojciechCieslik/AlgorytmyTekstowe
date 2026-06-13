import ollama as ol
import time
#import ragas
from ai.CulinaryResponse import CulinaryResponse, Crucial, ListCrucial


def test_model(model_name,iterations,user_rec_prompt,sys_rec_prompt):
    message = [{'role': 'system', 'content': sys_rec_prompt},
               {'role': 'user', 'content': user_rec_prompt}]
    format = CulinaryResponse.model_json_schema()
    options = {"temperature": 0}

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

def add_crucial_ingredients_test(model_name,user_ing_prompt,sys_ing_prompt):
    message = [{'role': 'system', 'content': sys_ing_prompt},
               {'role': 'user', 'content': user_ing_prompt}]
    format = ListCrucial.model_json_schema()
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

def add_crucial_ingredients(model_name,user_ing_prompt,sys_ing_prompt):
    message = [{'role': 'system', 'content': sys_ing_prompt},
               {'role': 'user', 'content': user_ing_prompt}]
    format = ListCrucial.model_json_schema()
    options = {"temperature":0}
    response = ol.chat(
        model=model_name,
        messages=message,
        format=format,
        options=options
    )
    return response['message']['content']



def get_agent_response(model_name, user_rec_prompt, sys_rec_prompt):
    """Zwraca odpowiedź agenta jako tekst (bez pętli i printów), idealne do automatyzacji."""
    message = [{'role': 'system', 'content': sys_rec_prompt},
               {'role': 'user', 'content': user_rec_prompt}]

    format_schema = CulinaryResponse.model_json_schema()
    options = {"temperature": 0.0}  # Temperatura 0 dla powtarzalności w testach!
    i= 0
    while True:
        response = ol.chat(
            model=model_name,
            messages=message,
            format=format_schema,
            options=options
        )
        print(response['message']['content'])
        if len(response['message']['content']) > 0:
            return response['message']['content']
        i+=1
        if i >= 1:
            return "Nie udało się znaleźć przepisu"
# passata, kurczak, wołowina, jajko, mleko, papryka, pomidory, kukurydza, fasola, ryż, chili, cukier, sól, papryka wędzona, cebula, czosnek, mąka
