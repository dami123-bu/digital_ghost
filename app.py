"""
app.py

Chainlit entrypoint for PharmaHelp.

Lifecycle:
  on_chat_start — build the LangGraph agent, store it in the user session
                  alongside a unique thread_id for InMemorySaver checkpointing.
  on_message    — pass the user's message to the graph and stream the reply. (doesnt stream reply)
"""

import uuid

import chainlit as cl
from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage

from pharma_help.agents.graph import build_graph


@cl.on_chat_start
async def on_chat_start() -> None:
    cl.user_session.set("graph", await build_graph())
    cl.user_session.set("thread_id", str(uuid.uuid4()))
    await cl.Message(content="Welcome to **PharmaHelp**. How can I assist you?").send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    graph = cl.user_session.get("graph")
    thread_id = cl.user_session.get("thread_id")
    config = {"configurable": {"thread_id": thread_id}}

    result = await graph.ainvoke(
        {"messages": [HumanMessage(content=message.content)]},
        config=config,
    )

    final_msg = result["messages"][-1]
    await cl.Message(content=final_msg.content).send()