from google import genai
import constants

client = genai.Client()

response = client.models.generate_content_stream(
    model= constants.MODEL_NAME,
    contents=["Explain how AI works"]
)
for chunk in response:
    print(chunk.text, end="")