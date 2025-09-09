import google.generativeai as genai
import os

# Make sure you have your API key in an environment variable
# or replace "YOUR_API_KEY" with your actual key.
# It's better practice to use environment variables.
# os.environ['GOOGLE_API_KEY'] = 'YOUR_API_KEY'

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Now you can use the library
model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content("Explain the difference between an API Key and OAuth2.")
print(response.text)
