"""
Given a query (like a linter finding), finds the most relevant
chunks from the PEP index using cosine similarity.

Cosine similarity measures how "aligned" two vectors are - the
same dot-product math from vector geometry, just comparing
word-importance vectors instead of physical vectors.
"""

import pickle
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

INDEX_FILE = Path("pep_index.pkl")


def load_index():
    with open(INDEX_FILE, "rb") as f:
        return pickle.load(f)


def retrieve_relevant_chunks(query, index, top_k=3):
    """Return the top_k chunks most relevant to the query."""
    vectorizer = index["vectorizer"]
    chunk_vectors = index["chunk_vectors"]
    chunks = index["chunks"]

    query_vector = vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, chunk_vectors)[0]

    # Get indices of the top_k highest similarity scores
    top_indices = similarities.argsort()[::-1][:top_k]

    results = []
    for i in top_indices:
        results.append({
            "chunk": chunks[i],
            "score": similarities[i],
        })
    return results


if __name__ == "__main__":
    # Quick manual test
    index = load_index()
    query = "blank lines between function definitions"
    results = retrieve_relevant_chunks(query, index)

    for r in results:
        print(f"\n--- score: {r['score']:.3f} ---")
        print(r["chunk"])