from dotenv import load_dotenv
import os
from zhipuai import ZhipuAI
from openai import OpenAI
import chainlit as cl

api_key = os.getenv('API_KEY')


client = ZhipuAI(api_key=api_key )  # 请填写您自己的API Key

settings = {
    "model": "glm-4-flash",
    "stream": True,
}

@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "你是一位博学多才的问答机器人."}],
    )

@cl.on_message
async def on_message(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})
    msg = cl.Message(content="")
    
    response = client.chat.completions.create(
        messages=[
            {
                "content": message.content,
                "role": "user"
            }
        ],
        **settings
    )
    
    for chunk in response:
        await msg.stream_token(chunk.choices[0].delta.content)
    message_history.append({"role": "assistant", "content": msg.content})
    await msg.update()