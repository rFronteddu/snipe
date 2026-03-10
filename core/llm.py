# core/llm.py
import ollama

class OllamaLLM:
    def __init__(self, model="llama3", host="http://localhost:11434"):
        self.model = model
        self.client = ollama.Client(host=host)

    def generate(self, prompt):
        response = self.client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )

        return response["message"]["content"]