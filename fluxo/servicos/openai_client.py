import os
import openai

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
