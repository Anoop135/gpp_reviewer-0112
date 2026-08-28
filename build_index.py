"""
Splits the PEP docs into small chunks and builds a TF-IDF index
over them, so we can later find the chunks most relevant to a
given code issue.

TF-IDF turns each chunk of text into a vector of numbers based on
which words appear and how distinctive they are. Finding the most
relevant chunk is then just a matter of comparing vectors with
cosine similarity - literally a dot product between two vectors,
same math as your JEE days, just applied to text instead of physics.
"""

import pickle
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer

DOCS_FOLDER = Path("pep_docs")
INDEX_FILE = Path("pep_index.pkl")

CHUNK_SIZE = 500  # characters per chunk


def chunk_text(text, chunk_size=CHUNK_SIZE):
    """Split text into overlapping chunks so context isn't lost at boundaries."""
    chunks = []
    overlap = 100
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def build_index():
    all_chunks = []
    chunk_sources = []  # tracks which file each chunk came from

    for doc_file in DOCS_FOLDER.glob("*.txt"):
        text = doc_file.read_text(encoding="utf-8")
        chunks = chunk_text(text)
        all_chunks.extend(chunks)
        chunk_sources.extend([doc_file.name] * len(chunks))

    print(f"Built {len(all_chunks)} chunks from {len(list(DOCS_FOLDER.glob('*.txt')))} docs.")

    vectorizer = TfidfVectorizer(stop_words="english")
    chunk_vectors = vectorizer.fit_transform(all_chunks)

    # Save everything we need for retrieval later
    with open(INDEX_FILE, "wb") as f:
        pickle.dump(
            {
                "vectorizer": vectorizer,
                "chunk_vectors": chunk_vectors,
                "chunks": all_chunks,
                "sources": chunk_sources,
            },
            f,
        )

    print(f"Index saved to {INDEX_FILE}")


if __name__ == "__main__":
    build_index()