import g4f
from g4f.client import Client

prompt = input("[prompt]>> ")

client = Client()

chat_completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
)

# 결과 출력
response_content = chat_completion.choices[0].message.content or ""
model = chat_completion.model  # model 정보
provider = chat_completion.provider if hasattr(chat_completion, 'provider') else "N/A"  # provider 정보

print(f"Provider: {provider}")
print(f"Model: {model}")
print(f"Response: {response_content}")