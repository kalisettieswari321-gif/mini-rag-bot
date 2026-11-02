import ollama
import os

MODEL = "qwen2.5:3b-instruct"

ollama_client = ollama.Client(
    host=os.getenv("OLLAMA_HOST", "http://localhost:11434")
)

def generate(prompt: str) -> str:
    response = ollama_client.generate(
        model=MODEL,
        prompt=prompt,
        options={"temperature": 0.2}
    )
    return response["response"].strip()
