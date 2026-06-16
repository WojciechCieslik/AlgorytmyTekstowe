from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

QUERY_PREFIX = "zapytanie: "


class RecipeEmbedder:
    def __init__(self, model_name: str = 'sdadas/mmlw-retrieval-roberta-large'):
        self.model = SentenceTransformer(model_name)
        self.dim = getattr(self.model, "get_embedding_dimension", getattr(self.model, "get_sentence_embedding_dimension"))()

    @staticmethod
    def _format_recipe_text(recipe_name: str, ingredient_names: List[str]) -> str:
        ing_str = ", ".join(sorted(set(ingredient_names)))
        return f"Aby przygotować {recipe_name} wymagane są następujące składniki: {ing_str}."

    @staticmethod
    def _format_query_text(user_ingredients: List[str]) -> str:
        ing_str = ", ".join(sorted(set(user_ingredients)))
        return f"{QUERY_PREFIX}Jakie przepisy można przygotować ze składników: {ing_str}?"

    def embed_recipe(self, recipe_name: str, ingredient_names: List[str]) -> np.ndarray:
        text = self._format_recipe_text(recipe_name, ingredient_names)
        return self.model.encode(text, normalize_embeddings=True)

    def embed_recipes(self, recipe_names: List[str], ingredients_list: List[List[str]]) -> np.ndarray:
        texts = [
            self._format_recipe_text(name, ing_names)
            for name, ing_names in zip(recipe_names, ingredients_list)
        ]
        return self.model.encode(texts, normalize_embeddings=True, show_progress_bar=True)

    def embed_query(self, user_ingredients: List[str]) -> np.ndarray:
        text = self._format_query_text(user_ingredients)
        return self.model.encode(text, normalize_embeddings=True)
