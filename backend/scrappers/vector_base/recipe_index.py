import lancedb
import pandas as pd
import numpy as np

from typing import List, Dict, Any

class RecipeIndex:
    def __init__(self, db_path: str = "memory://", table_name: str = "recipes"):
        self.db = lancedb.connect(db_path)
        self.table_name = table_name
        self.tbl = None

    def create_table(self, records: List[Dict[str, Any]], vectors: np.ndarray):
        if self.table_name in self.db.list_tables():
            self.db.drop_table(self.table_name)

        rows = []
        for rec, vec in zip(records, vectors):
            rows.append({
                "vector": vec.tolist(),
                "name": rec["recipe_name"],
                "url": rec["url"],
                "ingredients_full": ", ".join(rec["ingredients_full"]),
            })

        df = pd.DataFrame(rows)
        self.tbl = self.db.create_table(self.table_name, data=df, mode="overwrite")

    def search(self, query_vec: np.ndarray, k: int = 5) -> pd.DataFrame:
        """Wyszukiwanie kosinusowe (1 - dystans = podobieństwo)."""
        return self.tbl.search(query_vec.tolist()).metric("cosine").limit(k).to_pandas()
