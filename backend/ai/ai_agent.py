import ollama as ol
import time
#import ragas
from ai.CulinaryResponse import CulinaryResponse, Crucial, ListCrucial


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


def get_agent_response(model_name, user_rec_prompt, sys_rec_prompt):
    """Zwraca odpowiedź agenta jako tekst (bez pętli i printów), idealne do automatyzacji."""
    message = [{'role': 'system', 'content': sys_rec_prompt},
               {'role': 'user', 'content': user_rec_prompt}]

    format_schema = CulinaryResponse.model_json_schema()
    options = {"temperature": 0.0}  # Temperatura 0 dla powtarzalności w testach!

    response = ol.chat(
        model=model_name,
        messages=message,
        format=format_schema,
        options=options
    )

    return response['message']['content']
