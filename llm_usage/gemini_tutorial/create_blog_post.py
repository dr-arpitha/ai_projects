#https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started.ipynb
import requests
import pathlib
from PIL import Image
from google import genai
from google.genai.types import HttpOptions

from gemini_tutorial import constants

#Save an image into jetpack.png
IMG = "https://storage.googleapis.com/generativeai-downloads/data/jetpack.png" # @param {type: "string"}

img_bytes = requests.get(IMG).content

img_path = pathlib.Path('jetpack.png')
img_path.write_bytes(img_bytes)

#Write a blog post about the saved images
image = Image.open(img_path)
image.thumbnail([512,512])

client = genai.Client(http_options=HttpOptions(api_version="v1"))
response = client.models.generate_content(
    model=constants.MODEL_NAME,
    contents=[
        image,
        "Write a short and engaging blog post based on this picture."
    ]
)

print(response.text)

