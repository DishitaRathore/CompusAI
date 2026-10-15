import json
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
INDEX_PATH = BASE_DIR / "knowledge.index"
METADATA_PATH = BASE_DIR / "knowledge_metadata.json"

MODEL_NAME = "all-MiniLM-L6-v2"


def load_documents():
    documents = []

    for file_path in sorted(KNOWLEDGE_BASE_DIR.glob("*.txt")):
        text = file_path.read_text(encoding="utf-8").strip()

        if text:
            documents.append(
                {
                    "source": file_path.name,
                    "text": text
                }
            )

    return documents


def build_index():
    documents = load_documents()

    if not documents:
        raise RuntimeError(
            "No documents found inside the knowledge_base folder."
        )

    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    texts = [document["text"] for document in documents]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True
    ).astype("float32")

    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_PATH))

    METADATA_PATH.write_text(
        json.dumps(documents, indent=2),
        encoding="utf-8"
    )

    print(f"Built FAISS index with {len(documents)} documents.")


def search_documents(query: str, top_k: int = 2):
    if not INDEX_PATH.exists() or not METADATA_PATH.exists():
        raise RuntimeError(
            "Knowledge index not found. Run python rag.py first."
        )

    model = SentenceTransformer(MODEL_NAME)
    index = faiss.read_index(str(INDEX_PATH))

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    ).astype("float32")

    faiss.normalize_L2(query_embedding)

    scores, indexes = index.search(query_embedding, top_k)

    documents = json.loads(
        METADATA_PATH.read_text(encoding="utf-8")
    )

    results = []

    for score, document_index in zip(scores[0], indexes[0]):
        if document_index == -1:
            continue

        document = documents[int(document_index)]

        results.append(
            {
                "source": document["source"],
                "text": document["text"],
                "score": float(score)
            }
        )

    return results


def get_relevant_context(
    query: str,
    top_k: int = 2
) -> str:
    results = search_documents(
        query=query,
        top_k=top_k
    )

    if not results:
        return "No relevant information was found."

    context_parts = []

    for result in results:
        context_parts.append(
            f"Source: {result['source']}\n"
            f"{result['text']}"
        )

    return "\n\n".join(context_parts)

if __name__ == "__main__":
    build_index()