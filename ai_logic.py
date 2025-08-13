import openai
import os
from dotenv import load_dotenv

# Load OpenAI key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_ai_reply(message: str):
    prompt = f"""
You are NiveshSathi, a friendly Hindi+English financial assistant.
Understand user's financial questions and help with SIPs, loans, net worth, goals, investments.

User: {message}
Assistant:"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or gpt-4 if allowed
            messages=[
                {"role": "system", "content": "You are a helpful financial assistant that understands Hindi and English."},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ AI response failed: {str(e)}"
