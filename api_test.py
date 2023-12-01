import json
import aiohttp
import asyncio
from config import endpoint # импортируем из config переменные

async def fetch_completion(messages):
    messages = messages
    endpoint = endpoint
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': messages,
    }
    data = json.dumps(data)
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, headers=headers, data=data) as response:
            return await response.json()
        
async def user_text():
    return input()

async def main():
    messages = [
            {"role": "system", "content": "Instructions: You are Mario"},
            {"role": "user", "content": "Привет, как тебя зовут?"}
        ]
    while True:
        answer = await fetch_completion(messages)
        print(answer)
        try:
            answer_message = answer['choices'][0]['message']
        except KeyError:
            answer_message = answer[-1]['choices'][0]['message']
        print(answer_message)
        messages.append(answer_message)
        messages.append({'role': 'user', 'content': await user_text()})
        print(messages)
        





if __name__ == '__main__':
    asyncio.run(main())