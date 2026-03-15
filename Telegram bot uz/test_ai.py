import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"Testing API Key: {api_key[:10]}...")

try:
    genai.configure(api_key=api_key)
    print("Testing with system_instruction...")
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction="You are a helpful assistant."
    )
    response = model.generate_content("Hi")
    print(f"SUCCESS: {response.text}")
except Exception as e:
    print(f"FAILED: {e}")
