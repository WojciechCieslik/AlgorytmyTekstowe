from typing import Optional,List

from pydantic import BaseModel, HttpUrl

class CulinaryResponse(BaseModel):
    info: str
    found: bool
    dish_name: Optional[str] = None
    dish_link: Optional[str] = None


class ActualizedRecipe(BaseModel):
    url: str
    recipe_name: str
    ingredients: list[list[str]]
    crucial: list[str]


class Crucial(BaseModel):
    crucial_ingredients_for_recipes: list[list[str]]