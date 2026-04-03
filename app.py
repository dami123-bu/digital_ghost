import chainlit as cl


@cl.on_chat_start
async def on_chat_start() -> None:
    await cl.Message(content="Welcome to **PharmaHelp**. How can I assist you?").send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    await cl.Message(content=message.content).send()
