import g4f
from g4f.client   import Client

prompt = input(">> ")

client = Client()

chat_completion = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
)

print(chat_completion.choices[0].message.content or "")