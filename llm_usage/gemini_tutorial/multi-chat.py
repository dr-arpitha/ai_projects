from google import genai

# from gemini_tutorial import constants

client = genai.Client()
chat = client.chats.create(model="gemini-2.5-flash")

msg = chat.send_message("Tell me if Synergy Network is a nice name for AI tech company")
print(msg.text)

# msg = chat.send_message("Tell me if Synergy Network sums to 24 based on chaldean numerlogy")
# print(msg.text)

for message in chat.get_history() :
    print(message)
    print(f'role - {message.role}', end=": ")
    print(message.parts[0].text)