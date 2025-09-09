from google import genai
from google.genai.types import HttpOptions

# from gemini_tutorial import constants
MODEL_NAME="gemini-2.5-flash"
client = genai.Client(http_options=HttpOptions(api_version="v1"))

response = client.models.generate_content(
    model=MODEL_NAME,
    contents="Please give me a fast python library to generate simple UI for my app?",
)
print(response.text)
# Example response:
# Okay, let's break down how AI works. It's a broad field, so I'll focus on the ...
#
# Here's a simplified overview:
# ...
