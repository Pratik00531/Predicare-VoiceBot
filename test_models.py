from dotenv import load_dotenv
load_dotenv()

import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

try:
    models = client.models.list()
    print("Available models:")
    for model in models.data:
        if "vision" in model.id.lower() or "llama" in model.id.lower():
            print(f"- {model.id}")
except Exception as e:
    print(f"Error: {e}")
