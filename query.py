"""
Сұраққа жауап береді: аударма + векторлық іздеу + OpenAI жауабы.
"""

import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
STORE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db")
TOP_K = 5


def load_store(collection: str = "book") -> tuple[list[str], np.ndarray, str]:
    json_path = os.path.join(STORE_DIR, f"{collection}.json")
    npy_path = os.path.join(STORE_DIR, f"{collection}.npy")
    if not os.path.exists(json_path) or not os.path.exists(npy_path):
        raise ValueError(
            f"'{collection}' коллекциясы табылмады. "
            "Алдымен: python ingest.py <файл>"
        )
    with open(json_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    embeddings = np.load(npy_path)
    return meta["chunks"], embeddings, meta.get("source", "")


def cosine_similarity(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-10)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10
    return (matrix / norms) @ query_norm


def translate_to_english(text: str) -> str:
    """Сұрақты ағылшын тіліне аударады (retrieval үшін)."""
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": "Translate the following question to English. Return only the translation, nothing else."},
            {"role": "user", "content": text},
        ],
        temperature=0,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()


def get_query_embedding(query: str) -> np.ndarray:
    response = client.embeddings.create(model=EMBED_MODEL, input=[query])
    return np.array(response.data[0].embedding, dtype=np.float32)


def retrieve(query: str, collection: str = "book", top_k: int = TOP_K) -> list[dict]:
    chunks, embeddings, source = load_store(collection)

    # Сұрақты ағылшынша аударып, сол тілде іздейміз
    en_query = translate_to_english(query)

    query_vec = get_query_embedding(en_query)
    scores = cosine_similarity(query_vec, embeddings)
    top_indices = np.argsort(scores)[::-1][:top_k]

    return [
        {
            "text": chunks[i],
            "chunk_index": int(i),
            "source": source,
            "similarity": round(float(scores[i]), 4),
            "translated_query": en_query,
        }
        for i in top_indices
    ]


def answer(query: str, collection: str = "book", show_sources: bool = True) -> str:
    chunks = retrieve(query, collection)
    translated = chunks[0]["translated_query"]

    context = "\n\n---\n\n".join(
        f"[Чанк {c['chunk_index']}] {c['text']}" for c in chunks
    )

    system_prompt = (
        "Сен кітап мазмұнын талдайтын AI көмекшісің. "
        "Берілген контекст негізінде сұраққа нақты және толық жауап бер. "
        "Контекстте жоқ ақпаратты өз бетіңше ойлап таппа. "
        "Егер жауапты контекстен таба алмасаң, 'Кітапта бұл туралы ақпарат табылмады' деп жауап бер. "
        "Жауапты міндетті түрде сұрақ қойылған тілде бер."
    )

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Контекст:\n{context}\n\nСұрақ: {query}"},
        ],
        temperature=0.2,
    )

    reply = response.choices[0].message.content

    if show_sources:
        reply += f"\n\n---\n🔍 Аударылған іздеу: *{translated}*\n"
        for c in chunks:
            reply += f"\n  Чанк {c['chunk_index']} — ұқсастық: {c['similarity']}"

    return reply


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Қолдану: python query.py "сұрағыңыз"')
        sys.exit(1)
    question = " ".join(sys.argv[1:])
    print(f"\nСұрақ: {question}\n")
    print(answer(question))
