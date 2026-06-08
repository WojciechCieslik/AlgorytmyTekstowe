from typing import List, Dict, Any
from vector_base.recipe_embedder import RecipeEmbedder
from vector_base.recipe_index import RecipeIndex

class RecipeSearch:
    def __init__(self, embedder: RecipeEmbedder, index: RecipeIndex):
        self.embedder = embedder
        self.index = index

    def search(self, user_ingredients: List[str], k: int = 5) -> List[Dict[str, Any]]:
        if not user_ingredients:
            return []

        query_vec = self.embedder.embed_query(user_ingredients)
        df = self.index.search(query_vec, k=k)

        results = []
        for _, row in df.iterrows():
            results.append({
                'name': row['name'],
                'url': row['url'],
                'similarity': round(1.0 - row['_distance'], 4),
                'ingredients_full': row['ingredients_full'],
            })
        return results
