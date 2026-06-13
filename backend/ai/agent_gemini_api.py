

from google import genai
from google.genai import types
from ai.CulinaryResponse import CulinaryResponse, ListCrucial
import os
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
# Inicjalizacja nowego klienta.
# Najlepiej pobiera on klucz automatycznie ze zmiennej środowiskowej GEMINI_API_KEY.
# Jeśli wolisz wpisać na sztywno, użyj: client = genai.Client(api_key="TWÓJ_KLUCZ")
client = genai.Client(api_key=api_key)


def get_agent_response(model_name, user_rec_prompt, sys_rec_prompt):
    """Główny agent decyzyjny (Gemini - Nowa Składnia SDK)"""

    response = client.models.generate_content(
        model=model_name,
        contents=user_rec_prompt,
        config=types.GenerateContentConfig(
            system_instruction=sys_rec_prompt,
            response_mime_type="application/json",
            #response_schema=CulinaryResponse,
            temperature=0.0  # Zero halucynacji
        )
    )

    return response.text


def add_crucial_ingredients(model_name, user_ing_prompt, sys_ing_prompt):
    """Agent wyciągający kluczowe składniki (Gemini - Nowa Składnia SDK)"""

    response = client.models.generate_content(
        model=model_name,
        contents=user_ing_prompt,
        config=types.GenerateContentConfig(
            system_instruction=sys_ing_prompt,
            response_mime_type="application/json",
            #response_schema=ListCrucial,
            temperature=0.0
        )
    )

    return response.text