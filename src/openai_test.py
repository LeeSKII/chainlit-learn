import os
import chainlit as cl
from openai import AsyncOpenAI

api_key = os.getenv("API_KEY")

settings = {
    "model": "glm-4",
    "temperature": 0.7,
    "max_tokens": 5000,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}

client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

# Instrument the OpenAI client
cl.instrument_openai()

@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )

@cl.on_message 
async def chat(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    msg = cl.Message(content="")

    stream = await client.chat.completions.create(
        messages=message_history, stream=True, **settings
    )

    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await msg.stream_token(token)

    message_history.append({"role": "assistant", "content": msg.content})


if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)
