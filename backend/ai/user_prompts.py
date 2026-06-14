def get_user_ing_prompt(base):
    return f"""
        Oto dostępne przepisy:
        {base}
        Dodaj do bazy niezbędne składniki dla każdego z przepisów.
        """

def get_user_rec_prompt(ingredients,base,crucial_ing):
    return f"""
            Mam w lodówce: {ingredients}
    
            Oto przepisy, które znalazłem w mojej bazie oraz kluczowe dla nich składniki:
            ---
            {base}
            ---
    
            Oto kluczowe składniki potrzebne do stworzenia odpowiednich przepisów:
            {crucial_ing}
    
            Czy mogę coś z tego ugotować?
            Pod jakim linkiem znajdę przepis?
            """

def get_user_norm_prompt(user_ing):
    return f"Dokonaj normalizacji tych składników: {user_ing}"