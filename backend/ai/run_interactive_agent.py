import json
import time
from ai_agent import run_pipeline, init_db

def main():
    print("=========================================")
    print("       INTERAKTYWNY AGENT KUCHENNY       ")
    print("=========================================")
    
    # Inicjalizacja bazy raz przed główną pętlą (znaczne przyspieszenie)
    searcher = init_db()
    
    print("\nNapisz w jednym zdaniu co masz w lodówce i na co masz ochotę.")
    print("Wciśnij Enter, aby zatwierdzić (zakończyć wprowadzanie).")
    print("Aby zakończyć program, wpisz 'exit' lub wciśnij Ctrl+C.\n")

    while True:
        try:
            user_input = input("Twój prompt:\n> ")
        except (KeyboardInterrupt, EOFError):
            print("\nZakończono.")
            break
            
        if user_input.strip().lower() in ['exit', 'quit', 'wyjdź']:
            print("Zakończono.")
            break

        if not user_input.strip():
            print("Nie podano żadnych składników.\n")
            continue

        print("\nPrzetwarzanie (może to zająć chwilę)...")
        t1 = time.time()
        
        try:
            result = run_pipeline(user_input, searcher=searcher)
        except Exception as e:
            print(f"\nWystąpił błąd podczas działania AI: {e}\n")
            continue

        t2 = time.time()
        
        print("\n" + "="*41)
        print("                 WYNIK                   ")
        print("="*41)
        
        # Ładne wyświetlenie zamiast surowego JSONa
        info = result.get("info", "Brak podsumowania.")
        print(f"\n{info}\n")
        
        dishes = result.get("dishes", [])
        if dishes:
            print("Polecane przepisy:")
            for idx, dish in enumerate(dishes, 1):
                name = dish.get("dish_name", "Nieznane danie")
                link = dish.get("dish_link", "#")
                missing = dish.get("missing_ingredients", [])
                
                print(f" {idx}. {name}")
                print(f"    🔗 Link: {link}")
                if missing:
                    print(f"    ❌ Brakuje: {', '.join(missing)}")
                else:
                    print(f"    ✅ Masz wszystkie składniki!")
                print()
        else:
            print("Nie udało się znaleźć odpowiednich przepisów lub wystąpił błąd.")
            
        print(f"Czas przetwarzania: {t2-t1:.2f} s")
        print("=========================================\n")

if __name__ == '__main__':
    main()
