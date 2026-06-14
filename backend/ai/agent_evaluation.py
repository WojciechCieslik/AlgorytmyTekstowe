import json
import asyncio
import pandas as pd
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.embeddings import HuggingFaceEmbeddings as RagasHFEmbeddings

from ragas.metrics.collections import Faithfulness, AnswerRelevancy, AnswerCorrectness
from ragas.dataset_schema import SingleTurnSample

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 50)

print("1. Powoływanie Sędziego...")
ollama_client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

sedzia_llm = llm_factory(model="phi4:14b", client=ollama_client)
sedzia_embeddings = RagasHFEmbeddings(model='sdadas/mmlw-retrieval-roberta-large')

print("2. Ładowanie Złotego Zbioru Danych (Golden Dataset)...")

try:
    with open("test_dataset.json", "r", encoding="utf-8") as f:
        dane_z_testow = json.load(f)
except FileNotFoundError:
    print("BŁĄD: Nie znaleziono pliku 'test_dataset.json'. Uruchom najpierw dataset_generator.py!")
    exit()

samples = []
for item in dane_z_testow:

    samples.append(SingleTurnSample(
        user_input=item["user_input"],
        retrieved_contexts=item["retrieved_contexts"],
        response=item["response"],
        reference=item["reference"]
    ))

print("3. Inicjalizacja metryk i Sędziego...")
faithfulness_metric = Faithfulness(llm=sedzia_llm)
answer_relevancy_metric = AnswerRelevancy(llm=sedzia_llm, embeddings=sedzia_embeddings)
answer_correctness_metric = AnswerCorrectness(llm=sedzia_llm, embeddings=sedzia_embeddings)

async def run_eval():
    results = []
    for i, sample in enumerate(samples):
        print(f"  Oceniam próbkę {i + 1}/{len(samples)}...")

        faith = await faithfulness_metric.ascore(
            user_input=sample.user_input,
            response=sample.response,
            retrieved_contexts=sample.retrieved_contexts
        )

        rel = await answer_relevancy_metric.ascore(
            user_input=sample.user_input,
            response=sample.response
        )

        correctness = await answer_correctness_metric.ascore(
            user_input=sample.user_input,
            response=sample.response,
            reference=sample.reference
        )

        results.append({
            'test_id': f"Test_{i+1}",
            'faithfulness': faith,
            'answer_relevancy': rel,
            'answer_correctness': correctness
        })
    return pd.DataFrame(results)

df = asyncio.run(run_eval())

print("\n=== RAPORT Z EWALUACJI ===")
if 'answer_relevancy' in df.columns:
    df['answer_relevancy'] = df['answer_relevancy'].apply(lambda x: round(x.value, 4) if hasattr(x, 'value') else x)
if 'faithfulness' in df.columns:
    df['faithfulness'] = df['faithfulness'].apply(lambda x: round(x.value, 4) if hasattr(x, 'value') else x)
if 'answer_correctness' in df.columns:
    df['answer_correctness'] = df['answer_correctness'].apply(lambda x: round(x.value, 4) if hasattr(x, 'value') else x)

print(df[['test_id', 'faithfulness', 'answer_relevancy', 'answer_correctness']])