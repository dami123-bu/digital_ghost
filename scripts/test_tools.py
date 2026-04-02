from digital_ghost.agents.tools import retrieve_docs, synthesize_answer


def main() -> None:
    query = "What are the side effects of aspirin?"
    history = [{"role": "user", "content": query}]

    docs = retrieve_docs(query, k=2)
    answer = synthesize_answer(query, docs, history)

    print("Retrieved docs:")
    for doc in docs:
        print(doc)

    print("\nAnswer:")
    print(answer)


if __name__ == "__main__":
    main()