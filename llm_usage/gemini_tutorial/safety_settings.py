from IPython.display import Markdown
from google import genai
from google.genai.types import HttpOptions
from google.genai import types

from gemini_tutorial import constants

client  = genai.Client(http_options=HttpOptions(api_version="v1"))
prompt = """
    Write a list of 2 disrespectful things that I might say to the universe after stubbing my toe in the dark.
"""

safety_settings = [
    types.SafetySetting(
        category="HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold="BLOCK_ONLY_HIGH",
    ),
]

response = client.models.generate_content(
    model=constants.MODEL_NAME,
    contents=prompt,
    config=types.GenerateContentConfig(
        safety_settings=safety_settings,
    ),
)

print(response.text)
