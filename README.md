# 🍳 Kulinarny Agent AI (System RAG)

Inteligentny asystent kulinarny oparty na architekturze RAG (Retrieval-Augmented Generation). System analizuje składniki dostępne w lodówce użytkownika, przeszukuje wektorową bazę przepisów i przy pomocy lokalnych modeli językowych (LLM) decyduje, czy z dostępnych produktów można przygotować sensowny posiłek. Projekt posiada wbudowany, zautomatyzowany rurociąg ewaluacyjny oparty na bibliotece **Ragas**.

---

## 💻 Wymagania sprzętowe

Projekt opiera się na lokalnych modelach LLM (Ollama) oraz polskim modelu embeddingowym (Sentence Transformers). Aby system działał płynnie, zalecane są odpowiednie parametry sprzętowe:

* **Zalecane:**
    * **Karta graficzna (GPU):** min. 8 GB VRAM (np. NVIDIA RTX 3060 / 4060 lub lepsza). Dla `phi4:14b` zalecane 12 GB+ VRAM.
    * **RAM:** 16–32 GB.
* **Dysk:** ok. 15–20 GB wolnego miejsca na modele Ollama, embeddingowe oraz bazę wektorową.

---

## 🤖 Modele w projekcie

### Embeddingi i wyszukiwanie semantyczne
| Model | Rola | Gdzie używany |
|---|---|---|
| [`sdadas/mmlw-retrieval-roberta-large`](https://huggingface.co/sdadas/mmlw-retrieval-roberta-large) | Embedding przepisów i zapytań (1024 wymiary) | `recipe_embedder.py`, baza LanceDB |
| **LanceDB** | Indeks wektorowy i wyszukiwanie k-NN (cosine) | `recipe_index.py`, `recipe_search.py` |

Model embeddingowy pobierany jest automatycznie przy pierwszym uruchomieniu przez bibliotekę `sentence-transformers` (Hugging Face). **Nie instaluje się go przez Ollama.**

### Agenci LLM (główna aplikacja GUI / `recipe_logic.py`)
| Model | Rola |
|---|---|
| `qwen3:8b` | Normalizacja składników z lodówki |
| `qwen3:8b` | Wyciąganie kluczowych składników dla znalezionych przepisów |
| `phi4:14b` | Ostateczna decyzja: które danie można ugotować |

### Ewaluacja (Ragas)
| Model | Rola |
|---|---|
| `phi4:14b` | Model-sędzia w pipeline Ragas (`agent_evaluation.py`) |
| `sdadas/mmlw-retrieval-roberta-large` | Embeddingi w ewaluacji Ragas |

### Inne skrypty (opcjonalnie)
- `backend/main.py`, `dataset_generator.py` — mogą używać innych modeli Ollama do eksperymentów.
- `backend/main_api.py`, `agent_gemini_api.py` — wariant z API Gemini (wymaga osobnego klucza API).

---

## 🛠️ Wymagane oprogramowanie

1. **Python 3.13+**
2. **Ollama** — silnik do lokalnych modeli LLM ([ollama.com](https://ollama.com/))

Przed uruchomieniem aplikacji pobierz wymagane modele Ollama:

```bash
ollama pull qwen3:8b
ollama pull phi4:14b
```

| Model | Zastosowanie |
|---|---|
| `qwen3:8b` | Normalizacja składników + kluczowe składniki |
| `phi4:14b` | Decyzja końcowa + ewaluacja Ragas |

Upewnij się, że serwer Ollama działa w tle na domyślnym porcie `11434`.

---

## 🚀 Instalacja i uruchomienie

**1. Klonowanie repozytorium**
```bash
git clone https://github.com/WojciechCieslik/AlgorytmyTekstowe
cd AlgorytmyTekstowe
```

**2. Instalacja zależności**
```bash
pip install -r requirements.txt
```

**3. Uruchomienie GUI**
```bash
python frontend/gui_app.py
```

Przy pierwszym uruchomieniu aplikacja:
- pobierze model embeddingowy `sdadas/mmlw-retrieval-roberta-large`,
- zbuduje bazę wektorową w `backend/vector_base/vector_db/` z plików w `json_data/` (jeśli jeszcze nie istnieje).
