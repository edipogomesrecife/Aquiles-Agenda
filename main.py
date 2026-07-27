import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("Erro: GEMINI_API_KEY não encontrada!")
        return

    client = genai.Client(api_key=api_key)

    # Usando o nome exato da sua lista para o modelo Lite (leve e gratuito)
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents="Olá! Se estiver me ouvindo, responda apenas: Conectado com sucesso!",
    )

    print("\nResposta do Gemini:")
    print(response.text)

if __name__ == "__main__":
    main()