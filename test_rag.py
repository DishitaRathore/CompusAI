from rag import search_documents


TEST_QUERIES = [
    "What is the minimum attendance percentage?",
    "What should I do if I receive a suspicious email?",
    "How can students protect their accounts?",
    "Should passwords and private information be exposed?",
    "How can I check my remaining fee?"
]


def run_tests():
    for query in TEST_QUERIES:
        print("\n" + "=" * 60)
        print(f"Question: {query}")

        results = search_documents(
            query=query,
            top_k=1
        )

        if not results:
            print("No document found.")
            continue

        best_result = results[0]

        print(f"Retrieved source: {best_result['source']}")
        print(f"Similarity score: {best_result['score']:.4f}")
        print("Retrieved text:")
        print(best_result["text"][:300])


if __name__ == "__main__":
    run_tests()