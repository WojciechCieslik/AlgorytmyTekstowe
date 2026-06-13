# 🍳 Kulinarny Agent AI (System RAG)

Inteligentny asystent kulinarny oparty na architekturze RAG (Retrieval-Augmented Generation). System analizuje składniki dostępne w lodówce użytkownika, przeszukuje wektorową bazę przepisów i przy pomocy lokalnych modeli językowych (LLM) decyduje, czy z dostępnych produktów można przygotować sensowny posiłek. Projekt posiada wbudowany, zautomatyzowany rurociąg ewaluacyjny oparty na bibliotece **Ragas**.

---

## 💻 Wymagania sprzętowe

Projekt opiera się na lokalnie uruchamianych modelach LLM (np. Qwen 8B, Phi4 14B, Gemma4) oraz modelach Embeddingowych (RoBERTa). Aby system działał płynnie, zalecane są odpowiednie parametry sprzętowe:

* **Zalecane:**
    * **Karta graficzna (GPU):** Min. 8 GB VRAM (np. NVIDIA RTX 3060 / 4060 lub lepsza). Dla szybszego działania modeli 14B zalecane 12 GB+ VRAM.
    * **RAM:** 16 GB - 32 GB.
* **Dysk:** Ok. 15-20 GB wolnego miejsca na pobrane wagi modeli językowych i wektorowych.

---

## 🛠️ Wymagane oprogramowanie

1.  **Python 3.13+**
2.  **Ollama** – Silnik do uruchamiania lokalnych modeli LLM. (Pobierz z: [ollama.com](https://ollama.com/))

Przed uruchomieniem kodu upewnij się, że masz pobrane odpowiednie modele w Ollama. Otwórz terminal i wpisz:
* `ollama pull gemma4:latest` (Główny agent doradzający)
* `ollama pull qwen3:8b` (Agent do wyciągania kluczowych składników)
* `ollama pull phi4:14b` (Sędzia ewaluacyjny Ragas)

*(Upewnij się, że serwer Ollama działa w tle na domyślnym porcie `11434` podczas używania aplikacji).*

---

## 🚀 Instalacja i uruchomienie

**1. Klonowanie repozytorium**
```bash
git clone https://github.com/WojciechCieslik/AlgorytmyTekstowe
cd AlgorytmyTekstowe 
