"""
graph.py

LangGraph chat agent for PharmaHelp.
"""

from langchain_core.messages import SystemMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState

from pharma_help.config import OLLAMA_BASE_URL, OLLAMA_LLM_MODEL
from pharma_help.agents.retrieval import retrieve_docs

_SYSTEM_PROMPT = (
    "You are PharmaHelp, an AI assistant for pharmaceutical research at BioForge. "
    "Answer clearly and concisely using ONLY the provided PubMed context. "
    "Do not use prior knowledge. "
    "If the context is insufficient, say so. "
    "Cite claims with [S1], [S2], etc."
)


def _format_context(docs) -> str:
    if not docs:
        return "No PubMed context retrieved."

    blocks = []
    for i, doc in enumerate(docs, start=1):
        snippet = doc.content[:1200].strip()
        title = doc.title or "Untitled"

        blocks.append(
            f"[S{i}] Title: {title}\n"
            f"Score: {doc.score:.3f}\n"
            f"Content: {snippet}"
        )

    return "\n\n".join(blocks)


def _format_sources(docs) -> str:
    if not docs:
        return "\n\nSources:\n- No sources retrieved."

    lines = ["\n\nSources:"]
    for i, doc in enumerate(docs, start=1):
        title = doc.title or "Untitled"
        lines.append(f"- [S{i}] {title}")

    return "\n".join(lines)


def build_graph():
    llm = ChatOllama(model=OLLAMA_LLM_MODEL, base_url=OLLAMA_BASE_URL, think=False)

    async def generate(state: MessagesState) -> dict:
        print("RAG HIT")

        latest_user_msg = state["messages"][-1].content
        docs = []

        try:
            docs = retrieve_docs(latest_user_msg, k=5)
            context = _format_context(docs)
        except Exception as e:
            context = f"Retrieval failed: {e}"

        rag_prompt = (
            f"{_SYSTEM_PROMPT}\n\n"
            f"PubMed context:\n{context}\n\n"
            "Answer the user question using only the context above."
        )

        messages = [SystemMessage(content=rag_prompt)] + state["messages"]
        response = await llm.ainvoke(messages)

        response.content = response.content + _format_sources(docs)

        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("generate", generate)
    builder.add_edge(START, "generate")
    builder.add_edge("generate", END)

    return builder.compile(checkpointer=InMemorySaver())