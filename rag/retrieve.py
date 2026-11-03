import sqlite3
import sqlite_vec
import json
from typing import List, Tuple
from sentence_transformers import SentenceTransformer

DB_PATH = "db/rag.db"

model = SentenceTransformer("all-MiniLM-L6-v2")


def retrieve_with_sources(query: str, k: int = 4) -> Tuple[str, List[str]]:
    """
    Returns:
      - context_text: the top-k matching chunks joined together (sent to the LLM)
      - sources: unique file names those chunks came from (shown to the user)
    """
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)

    # Encode + serialize embedding
    embedding = model.encode(query).tolist()
    embedding_json = json.dumps(embedding)

    rows = conn.execute("""
        SELECT d.content, d.source
        FROM embeddings e
        JOIN documents d ON d.id = e.rowid
        WHERE e.embedding MATCH json(?)
        AND k = ?
        ORDER BY e.distance
    """, (embedding_json, k)).fetchall()

    conn.close()

    context_text = "\n\n".join([r[0] for r in rows])

    # Unique file names, keeping the order of best match first
    sources = []
    for r in rows:
        if r[1] not in sources:
            sources.append(r[1])

    return context_text, sources


def retrieve(query: str, k: int = 4) -> str:
    """Original function kept as it was: returns only the context text."""
    context_text, _ = retrieve_with_sources(query, k)
    return context_text