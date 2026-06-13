from typing import Optional,List

from pydantic import BaseModel, HttpUrl

class NormalizedIngredients(BaseModel):
    ingredients: List[str]

class MatchingDish(BaseModel):
    dish_name: str
    dish_link: str
    missing_ingredients: List[str]

class CulinaryResponse(BaseModel):
    info: str
    found: bool
    dishes: List[MatchingDish] = []


class ActualizedRecipe(BaseModel):
    url: str
    recipe_name: str
    ingredients: list[list[str]]
    crucial: list[str]


class Crucial(BaseModel):
    crucial_ingredients_for_recipes: dict[str, list[str]]