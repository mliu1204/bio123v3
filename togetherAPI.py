from together import Together
from dotenv import load_dotenv
import os

def callTogether(query):
    load_dotenv()
    api_key = os.getenv("TOGETHER_API_KEY")

    client = Together(api_key=api_key)

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=[{"role": "user", "content": "respond in a succinte manner to the following inquery: " + query}],
    )
    return response.choices[0].message.content