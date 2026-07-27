import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Instruções do Sistema para moldar a personalidade e lógica do Aquiles
SYSTEM_INSTRUCTION = """
Você é o Aquiles, o assistente inteligente de agenda do AURA OS.

REGRAS DE COMPORTAMENTO E RESPOSTAS:
1. Se o usuário perguntar se você consegue criar uma tarefa (ou demonstrar intenção de criar),
   confirme com entusiasmo e PEÇA os detalhes necessários (ex: título, data e horário).
   Exemplo: "Consigo sim! Qual é o título da tarefa e para qual data e horário você deseja agendar?"

2. Se o usuário fornecer as informações da tarefa (ex: "Criar reunião hoje às 15h"),
   confirme que a tarefa foi anotada com sucesso exibindo os dados informados.

3. Só diga que analisou/verificou a agenda quando o usuário pedir explicitamente para
   CONSULTAR, VER ou LISTAR os compromissos cadastrados.

4. Mantenha um tom prestativo, moderno, amigável e direto.
"""

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Erro: GEMINI_API_KEY não foi encontrada!")
        return

    # Inicializa o cliente oficial da API
    client = genai.Client(api_key=api_key)

    # Cria a sessão de chat mantendo o histórico de conversas e as instruções de sistema
    chat = client.chats.create(
        model="gemini-3.1-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.7,
        )
    )

    print("==================================================")
    print("🤖 Aquiles AI - Assistente do AURA OS (Iniciado)")
    print("Digite 'sair' a qualquer momento para encerrar.")
    print("==================================================\n")

    while True:
        try:
            mensagem_usuario = input("Você: ").strip()
            
            if not mensagem_usuario:
                continue

            if mensagem_usuario.lower() in ["sair", "exit", "quit"]:
                print("\nAquiles: Até logo! Se precisar da agenda, é só chamar.")
                break

            # Envia a mensagem para a IA mantendo o contexto da conversa
            response = chat.send_message(mensagem_usuario)
            
            print(f"\nAquiles: {response.text}\n")

        except Exception as e:
            print(f"\nOcorreu um erro na comunicação: {e}\n")

if __name__ == "__main__":
    main()
