import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
modelo = os.getenv("GEMINI_MODEL")
cliente = genai.Client()

resposta = cliente.models.generate_content(
    model=modelo,
    contents= "Diga que o teste de conexao deu certo como se fosse um radio sincronizando"
)

print(f"Modelo: {modelo}\n\n{resposta.text}")