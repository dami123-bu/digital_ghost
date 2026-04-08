"""
app.py

Chainlit entrypoint for PharmaHelp.

Lifecycle:
  on_chat_start — build the LangGraph agent, store it in the user session
                  alongside a unique thread_id for MemorySaver checkpointing.
  on_message    — pass the user's message to the agent and stream the reply.
"""

import chainlit as cl
from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from config import OLLAMA_BASE_URL, OLLAMA_LLM_MODEL

_SYSTEM_PROMPT = (
    "You are PharmaHelp, an AI assistant for pharmaceutical research at BioForge. "
    "Answer clearly and concisely."
)


@cl.on_chat_start
async def on_chat_start() -> None:
    llm = ChatOllama(model=OLLAMA_LLM_MODEL, base_url=OLLAMA_BASE_URL, think=False)
    cl.user_session.set("llm", llm)
    cl.user_session.set("history", [])
    await cl.Message(content="Welcome to **PharmaHelp**. How can I assist you?").send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    llm = cl.user_session.get("llm")
    history = cl.user_session.get("history")

    history.append(HumanMessage(content=message.content))
    messages = [SystemMessage(content=_SYSTEM_PROMPT)] + history

    msg = cl.Message(content="")
    await msg.send()

    full_content = ""
    async for chunk in llm.astream(messages):
        await msg.stream_token(chunk.content)
        full_content += chunk.content

    await msg.update()

    history.append(AIMessage(content=full_content))
    cl.user_session.set("history", history)
