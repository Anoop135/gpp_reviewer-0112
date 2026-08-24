from anthropic import Anthropic

client = Anthropic()
message = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1500,
    messages=[{"role": "user", "content": "Who is Osama bin Laden?"}],
)
print(message.content[0].text)