from digital_ghost.agents.session import SessionState


def main() -> None:
    session = SessionState()

    session.add_user_message("What are the side effects of aspirin?")
    session.add_assistant_message("Common side effects include stomach upset.")
    session.add_memory("User is asking about aspirin.")
    session.add_retrieved_docs(["doc1", "doc2"])

    print("History:")
    for msg in session.history:
        print(msg)

    print("\nMemory:")
    print(session.memory)

    print("\nRetrieved docs:")
    print(session.retrieved_docs)


if __name__ == "__main__":
    main()