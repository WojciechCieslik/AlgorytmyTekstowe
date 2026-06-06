import pandas as pd


def get_ingredients(soup):
    ingredients = soup.find_all(class_="ingredient")
    quantities = soup.find_all(class_="qty")
    #print(ingredients,"\n\n\n")

    result_ingredients = []
    for i,child in enumerate(ingredients):
        for kind in child.children:
            for qty in quantities[i].children:
                result_ingredients.append([kind,qty])
    return result_ingredients


def get_category(soup):
    cat = soup.find(class_="post-categories")
    return next(cat.a.children,None)


def get_title(soup):
    tit = soup.find('h1')
    return next(tit.children,None)


# link tytuł, składniki
# url, name, ingredients {składnik : jednostka}