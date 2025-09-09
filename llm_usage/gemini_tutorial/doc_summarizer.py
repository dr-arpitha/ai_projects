import httpx
from google import genai
from google.genai import types

docName = "https://discovery.ucl.ac.uk/id/eprint/10089234/1/343019_3_art_0_py4t4l_convrt.pdf"

doc_data = httpx.get(docName).content

prompt = "Summarize this document"
client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents= [
        types.Part.from_bytes(
        data=doc_data,
        mime_type='application/pdf',
      ),prompt]
    )

print(response.text)