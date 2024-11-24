from zhipuai import ZhipuAI
import os

api_key = os.getenv('API_KEY')

client = ZhipuAI(api_key=api_key )

def add(first,second):
    return {'result':first+second}

def divide(first,second):
    return {'result':first/second}


response = client.chat.completions.create(
    model="glm-4-plus",  # 填写需要调用的模型编码
    messages=[
        {"role": "user", "content": "6/2的结果再加上100的结果是多少?"},

    ],
    tools=[ 
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
)

print(response)