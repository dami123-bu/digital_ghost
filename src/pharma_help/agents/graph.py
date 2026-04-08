"""
graph.py

LangGraph chat agent for PharmaHelp.

Graph shape:  START -> generate -> END

The generate node calls ChatOllama with the full accumulated message history.
InMemorySaver checkpoints state per thread_id, so conversation history persists
across turns within a session without the caller needing to track it.

RAG hook: when ready, add a retrieve node before generate and extend
MessagesState with a context key.
"""

from langchain_core.messages import SystemMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState

from config import OLLAMA_BASE_URL, OLLAMA_LLM_MODEL

_SYSTEM_PROMPT = (
    "You are PharmaHelp, an AI assistant for pharmaceutical research at BioForge. "
    "Answer clearly and concisely. Acknowledge uncertainty where appropriate."
)


def build_graph():
    """Build and return a compiled LangGraph graph with InMemorySaver checkpointing.

    Each call returns an independent graph with its own InMemorySaver instance,
    so Chainlit sessions are fully isolated.

    Returns:
        CompiledStateGraph ready for async streaming via astream().
    """
    llm = ChatOllama(model=OLLAMA_LLM_MODEL, base_url=OLLAMA_BASE_URL, think=False)

    async def generate(state: MessagesState) -> dict:
        messages = [SystemMessage(content=_SYSTEM_PROMPT)] + state["messages"]
        response = await llm.ainvoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("generate", generate)
    builder.add_edge(START, "generate")
    builder.add_edge("generate", END)

    return builder.compile(checkpointer=InMemorySaver())
