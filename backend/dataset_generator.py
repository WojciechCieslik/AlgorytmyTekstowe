import json

from vector_base.recipe_embedder import RecipeEmbedder
from vector_base.recipe_index import RecipeIndex
from vector_base.recipe_search import RecipeSearch
from ai.ai_agent import add_crucial_ingredients, get_agent_response
from ai.system_prompts import crucial_ingredients_system_prompt as sys_ing_prompt, \
    finding_recipe_system_prompt as sys_rec_prompt


def main():
    print("1. Ładowanie bazy wektorowej...")
    # Upewnij się, że ścieżka do bazy jest poprawna względem uruchamiania
    vector_db = RecipeIndex(db_path="vector_base/vector_db")
    embedder = RecipeEmbedder()
    searcher = RecipeSearch(embedder, vector_db)


    model_crucial = 'qwen3:8b'
    gemma_strong = 'gemma4:12b'
    qwen_norm = 'qwen3:8b'
    qwen_strong = 'qwen3:14b'
    gemma = 'gemma4:latest'

    phi = 'phi4:14b'
    models = [model_crucial ,  gemma_strong  ,qwen_strong ,phi]
    for model_agent in models:


        # model_agent = 'gemma4:latest'

        testowe_lodowki = {
            # KATEGORIA 1: IDEALNE DOPASOWANIA
            "1_schabowy": ["schab", "jajka", "bułka tarta", "smalec", "sól", "pieprz", "ziemniaki"],
            "2_nalesniki": ["mąka pszenna", "mleko", "jajka", "woda", "olej", "sól"],

            # KATEGORIA 2: PUŁAPKI NA BRAKUJĄCY SKŁADNIK (Brak bazy)
            "3_kopytka_brak_maki": ["ziemniaki", "jajka", "sól", "masło", "boczek"],
            "4_paella_brak_ryzu": ["pierś z kurczaka", "krewetki", "groszek", "cebula", "czosnek", "pomidory"],

            # KATEGORIA 3: SZUM INFORMACYJNY I NADMIAR
            "5_szum": ["truskawki", "czosnek", "boczek", "czekolada", "musztarda"],
            "6_tylko_przyprawy": ["sól", "pieprz", "olej", "ocet", "cukier", "woda", "musztarda"],

            # KATEGORIA 4: DANIA SPECJALISTYCZNE / MAŁO SKŁADNIKÓW
            "7_sniadanie": ["jajka", "masło", "sól", "szczypiorek"],
            "8_dorsz": ["filet z dorsza", "czosnek", "masło klarowane", "cytryna", "szpinak baby"],

            # KATEGORIA 5: ZŁE ZAPYTANIA OD UŻYTKOWNIKA
            "9_literowki": ["muka pszenna", "smiotana", "rzułtka", "proszek d pieczenia"],
            "10_puste": ["null", "nic", "pusto", "woda"]
        }

        raw_dataset = []

        print("2. Rozpoczynam generowanie zestawu testowego...")
        for test_name, ingredients in testowe_lodowki.items():
            print(f" -> Przetwarzam: {test_name}")

            # Wyszukiwanie w bazie
            baza_wyniki = searcher.search(ingredients, k=5)
            baza_str = json.dumps(baza_wyniki, ensure_ascii=False)

            # Przekształcamy wyniki z bazy na listę stringów dla Ragas
            contexts_list = [f"Przepis na {res['name']}. Składniki: {res['ingredients_full']}" for res in baza_wyniki]

            # Pobieranie kluczowych składników
            user_ing_prompt = f"Oto dostępne przepisy:\n{baza_str}\nDodaj do bazy niezbędne składniki dla każdego z przepisów."
            crucial_ing = add_crucial_ingredients(model_crucial, user_ing_prompt, sys_ing_prompt)

            #Decyzja ostateczna
            user_rec_prompt = f"""
            Mam w lodówce: {ingredients}
            Oto przepisy, które znalazłem w mojej bazie oraz kluczowe dla nich składniki:
            ---
            {baza_str}
            ---
            Oto kluczowe składniki dla każdego z przepisów:
            {crucial_ing}
            Czy mogę coś z tego ugotować?
            """
            agent_response = get_agent_response(model_agent, user_rec_prompt, sys_rec_prompt)


            sample = {
                "test_id": test_name,
                "user_input": f"Mam w lodówce: {ingredients}",
                "retrieved_contexts": contexts_list,
                "response": agent_response,
                "reference": ""
            }
            raw_dataset.append(sample)


        output_file = f"ai/{model_agent}_test_dataset.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(raw_dataset, f, ensure_ascii=False, indent=4)

        print(f"\nGotowe! Wygenerowano plik '{output_file}'. Otwórz go i uzupełnij pole 'reference'!")


if __name__ == '__main__':
    main()