from pharma_help.agents.session import SessionState
from pharma_help.agents.tools import retrieve_docs, synthesize_answer


def main() -> None:
    session = SessionState()

    print("Multi-turn chat started. Type 'exit' to quit.\n")

    while True:
        user_input = input("User: ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        if not user_input:
            continue

        session.add_user_message(user_input)

        docs = retrieve_docs(user_input, k=2)
        session.add_retrieved_docs(docs)

        answer = synthesize_answer(
            query=user_input,
            docs=docs,
            history=session.recent_history(),
        )

        session.add_assistant_message(answer)

        print(f"Assistant: {answer}\n")


if __name__ == "__main__":
    main()