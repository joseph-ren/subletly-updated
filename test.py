from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key=API_KEY)

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents="Explain how AI works in a few words"
)
print(response.text)