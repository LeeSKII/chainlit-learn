from json import tool
from urllib import response
from dotenv import load_dotenv
import os
from zhipuai import ZhipuAI
from openai import OpenAI
import chainlit as cl
import json

api_key = os.getenv('API_KEY')


client = ZhipuAI(api_key=api_key )  # 请填写您自己的API Key

settings = {
    "model": "glm-4-flash",
    "stream": True,
    "tools":[ 
        {
            'type': 'function',
            'function': {
            'name': 'add',
            'description': '获取两个数相加的结果',
            'parameters': {
                'type': 'object',
                'properties': {
                'first': {
                    'type': 'number',
                    'description': '第一个数字',
                },
                'second': {
                    'type': 'number',
                    'description': '第二个数字',
                    },
                },
                'required': ['first', 'second'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
            'name': 'divide',
            'description': '获取两个数相除的结果',
            'parameters': {
                'type': 'object',
                'properties': {
                'first': {
                    'type': 'number',
                    'description': '被除数',
                },
                'second': {
                    'type': 'number',
                    'description': '除数',
                    },
                },
                'required': ['first', 'second'],
                },
            },
        },
    ]
}

def add(first,second):
    return {'result':first+second}

def divide(first,second):
    return {'result':first/second}

# @cl.set_starters
# async def set_starters():
#     return [
#         cl.Starter(
#             label="Morning routine ideation",
#             message="Can you help me create a personalized morning routine that would help increase my productivity throughout the day? Start by asking me about my current habits and what activities energize me in the morning.",
#             icon="/public/idea.svg",
#             ),

#         cl.Starter(
#             label="Explain superconductors",
#             message="Explain superconductors like I'm five years old.",
#             icon="/public/learn.svg",
#             ),
#         cl.Starter(
#             label="Python script for daily email reports",
#             message="Write a script to automate sending daily email reports in Python, and walk me through how I would set it up.",
#             icon="/public/terminal.svg",
#             ),
#         cl.Starter(
#             label="Text inviting friend to wedding",
#             message="Write a text asking a friend to be my plus-one at a wedding next month. I want to keep it super short and casual, and offer an out.",
#             icon="/public/write.svg",
#             )
#         ]

async def prase_function_call(msg,model_response,messages):
    tool_calls = model_response.choices[0].delta.tool_calls
    print("tool_calls",tool_calls)
    for tool_call in tool_calls:
        function_result = None
        if tool_call.function.name == 'add':
            args = tool_call.function.arguments
            function_result = add(**json.loads(args))
        elif tool_call.function.name == 'divide':
            args = tool_call.function.arguments
            function_result = divide(**json.loads(args))
        messages.append({
                "role": "tool",
                "content": f"{json.dumps(function_result)}",
                "tool_call_id":tool_call.id
            })
        response = client.chat.completions.create(
            messages=messages,
            **settings
        )
        for chunk in response:
            if chunk.choices[0].delta.tool_calls:
                await prase_function_call(msg,chunk,messages)
            else:
                await msg.stream_token(chunk.choices[0].delta.content)

@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "你是一位善于使用工具的问答机器人."}],
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
        if chunk.choices[0].delta.tool_calls:
            await prase_function_call(msg,chunk,message_history)
        else:
            await msg.stream_token(chunk.choices[0].delta.content)
    message_history.append({"role": "assistant", "content": msg.content})
    await msg.update()