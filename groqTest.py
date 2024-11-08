from groq import Groq


prompt = input(">> ")

client = Groq(api_key="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")
completion = client.chat.completions.create(
    model="gemma2-9b-it",
    messages=[
        {
            "role": "user",
            "content": prompt
        },
    ],
    temperature=1,
    max_tokens=4500,
    top_p=1,
    stream=False,
    stop=None,
)

print(completion.choices[0].message)
