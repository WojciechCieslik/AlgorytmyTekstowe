import time

import ollama as ol

from backend.ai.CulinaryResponse import CulinaryResponse, Crucial, NormalizedIngredients

OLLAMA_TIMEOUT_SEC = 180.0


def _chat(model_name, messages, format_schema=None, options=None, timeout=OLLAMA_TIMEOUT_SEC):
    client = ol.Client(timeout=timeout)
    opts = {"temperature": 0, "num_predict": 2048}
    if options:
        opts.update(options)
    if "qwen3" in model_name.lower():
        opts["think"] = False

    kwargs = {
        "model": model_name,
        "messages": messages,
        "options": opts,
    }
    if format_schema is not None:
        kwargs["format"] = format_schema

    try:
        response = client.chat(**kwargs)
    except Exception:
        if opts.pop("think", None) is not None:
            kwargs["options"] = opts
            response = client.chat(**kwargs)
        else:
            raise

    return response["message"]["content"]


def add_crucial_ingredients(model_name, user_ing_prompt, sys_ing_prompt):
    message = [
        {"role": "system", "content": sys_ing_prompt},
        {"role": "user", "content": user_ing_prompt},
    ]
    return _chat(model_name, message, format_schema=Crucial.model_json_schema())


def normalize_ingredients(model_name, user_prompt, sys_prompt):
    message = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_prompt},
    ]
    return _chat(model_name, message, format_schema=NormalizedIngredients.model_json_schema())


def get_agent_response(model_name, user_rec_prompt, sys_rec_prompt):
    message = [
        {"role": "system", "content": sys_rec_prompt},
        {"role": "user", "content": user_rec_prompt},
    ]
    format_schema = CulinaryResponse.model_json_schema()

    for _ in range(2):
        content = _chat(model_name, message, format_schema=format_schema, timeout=300.0)
        if content and content.strip():
            return content

    return '{"found": false, "info": "Nie udalo sie uzyskac odpowiedzi od modelu.", "dishes": []}'


def test_model(model_name, iterations, user_rec_prompt, sys_rec_prompt):
    message = [
        {"role": "system", "content": sys_rec_prompt},
        {"role": "user", "content": user_rec_prompt},
    ]
    format_schema = CulinaryResponse.model_json_schema()

    for i in range(iterations):
        t1 = time.time()
        print(f"Iteracja {i + 1}")
        content = _chat(model_name, message, format_schema=format_schema)
        t2 = time.time()
        print(content)
        print("czas: ", t2 - t1)
        print("")


def add_crucial_ingredients_test(model_name, user_ing_prompt, sys_ing_prompt):
    message = [
        {"role": "system", "content": sys_ing_prompt},
        {"role": "user", "content": user_ing_prompt},
    ]
    t1 = time.time()
    content = _chat(
        model_name,
        message,
        format_schema=Crucial.model_json_schema(),
        options={"temperature": 1},
    )
    t2 = time.time()
    print("czas: ", t2 - t1)
    print("")
    return content
