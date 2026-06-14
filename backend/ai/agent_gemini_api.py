

from google import genai
from google.genai import types
from ai.CulinaryResponse import CulinaryResponse, Crucial,NormalizedIngredients
import os
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)



def _clean_schema(schema: dict) -> dict:
    defs = schema.get("$defs", {})

    def _inline_refs(obj):
        if isinstance(obj, dict):
            if "$ref" in obj:

                ref_name = obj["$ref"].split("/")[-1]
                resolved = defs.get(ref_name, obj)
                return _inline_refs(resolved)
            return {k: _inline_refs(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_inline_refs(i) for i in obj]
        return obj


    inlined = _inline_refs(schema)

    unsupported = {"additionalProperties", "$defs", "$ref", "title", "default"}

    def _strip(obj):
        if isinstance(obj, dict):
            return {k: _strip(v) for k, v in obj.items() if k not in unsupported}
        elif isinstance(obj, list):
            return [_strip(i) for i in obj]
        return obj

    return _strip(inlined)


def _clean_response(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text[text.index("\n") + 1:] if "\n" in text else text
    if text.endswith("```"):
        text = text[:text.rfind("```")]
    return text.strip()

def normalize_ingredients(model_name, user_rec_prompt, sys_rec_prompt):
    schema = _clean_schema(NormalizedIngredients.model_json_schema())
    response = client.models.generate_content(
        model=model_name,
        contents=user_rec_prompt,
        config=types.GenerateContentConfig(
            system_instruction=sys_rec_prompt,
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.0
        )
    )
    return _clean_response(response.text)


def get_agent_response(model_name, user_rec_prompt, sys_rec_prompt):
    schema = _clean_schema(CulinaryResponse.model_json_schema())
    response = client.models.generate_content(
        model=model_name,
        contents=user_rec_prompt,
        config=types.GenerateContentConfig(
            system_instruction=sys_rec_prompt,
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.0  # Zero halucynacji
        )
    )
    return _clean_response(response.text)


def add_crucial_ingredients(model_name, user_ing_prompt, sys_ing_prompt):
    schema = _clean_schema(Crucial.model_json_schema())
    response = client.models.generate_content(
        model=model_name,
        contents=user_ing_prompt,
        config=types.GenerateContentConfig(
            system_instruction=sys_ing_prompt,
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.0
        )
    )
    return _clean_response(response.text)