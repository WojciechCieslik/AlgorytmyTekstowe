from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

class RecipeEmbedder:
    def __init__(self, model_name: str = 'sdadas/mmlw-retrieval-roberta-large'):
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()

    def embed_recipe(self, recipe_name: str, ingredient_names: List[str]) -> np.ndarray:
        ing_str = ", ".join(sorted(set(ingredient_names)))
        text = f"Nazwa: {recipe_name}. Składniki: {ing_str}"
        return self.model.encode(text, normalize_embeddings=True)

    def embed_query(self, user_ingredients: List[str]) -> np.ndarray:
        text = f"Składniki: {', '.join(sorted(set(user_ingredients)))}"
        return self.model.encode(text, normalize_embeddings=True)
