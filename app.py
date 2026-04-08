"""
app.py

Chainlit entrypoint for PharmaHelp.

Lifecycle:
  on_chat_start — build the LangGraph agent, store it in the user session
                  alongside a unique thread_id for InMemorySaver checkpointing.
  on_message    — pass the user's message to the graph and stream the reply.
"""

import uuid

import chainlit as cl
from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage

from pharma_help.agents.graph import build_graph


@cl.on_chat_start
async def on_chat_start() -> None:
    cl.user_session.set("graph", build_graph())
    cl.user_session.set("thread_id", str(uuid.uuid4()))
    await cl.Message(content="Welcome to **PharmaHelp**. How can I assist you?").send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    graph = cl.user_session.get("graph")
    thread_id = cl.user_session.get("thread_id")
    config = {"configurable": {"thread_id": thread_id}}

    msg = cl.Message(content="")
    await msg.send()

    async for event in graph.astream_events(
        {"messages": [HumanMessage(content=message.content)]},
        config=config,
        version="v2",
    ):
        if event["event"] == "on_chat_model_stream":
            token = event["data"]["chunk"].content
            if token:
                await msg.stream_token(token)

    await msg.update()
