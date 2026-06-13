from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

class RecipeEmbedder:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.dim = getattr(self.model, "get_embedding_dimension", getattr(self.model, "get_sentence_embedding_dimension"))()

    def embed_recipe(self, recipe_name: str, ingredient_names: List[str]) -> np.ndarray:
        ing_str = ", ".join(sorted(set(ingredient_names)))
        text = f"Składniki: {ing_str}"
        return self.model.encode(text, normalize_embeddings=True)

    def embed_recipes(self, recipe_names: List[str], ingredients_list: List[List[str]]) -> np.ndarray:
        texts = []
        for name, ing_names in zip(recipe_names, ingredients_list):
            ing_str = ", ".join(sorted(set(ing_names)))
            texts.append(f"Składniki: {ing_str}")
        return self.model.encode(texts, normalize_embeddings=True, show_progress_bar=True)

    def embed_query(self, user_ingredients: List[str]) -> np.ndarray:
        text = f"Składniki: {', '.join(sorted(set(user_ingredients)))}"
        return self.model.encode(text, normalize_embeddings=True)
