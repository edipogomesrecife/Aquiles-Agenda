import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)

# --- CONFIGURAÇÃO DE SEGURANÇA DO CORS ---
# Permite requisições APENAS do seu GitHub Pages e de ambientes locais de teste
ALLOWED_ORIGINS = [
    "https://edipogomesrecife.github.io",  # Domínio do seu GitHub Pages
    "http://localhost:3000",                # Permite testes locais
    "http://127.0.0.1:5500"                 # Permite Live Server do VS Code
]

# Restringe o acesso aos recursos do servidor apenas às origens acima
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})

# Lê a API Key que você cadastrou nas Environment Variables do Render
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

SYSTEM_INSTRUCTION = """Você é o Aquiles, assistente do AURA OS.
Se o usuário solicitar a criação de uma tarefa, responda estritamente em formato JSON válido com os seguintes campos:
{
  "action": "CREATE_TASK",
  "title": "Título da tarefa",
  "start": "HH:MM" (ou "" se não informado),
  "end": "HH:MM" (ou "" se não informado),
  "notes": "Notas ou descrição" (ou ""),
  "reply": "Mensagem confirmando a criação da tarefa"
}

Para mensagens normais (dúvidas ou conversas), responda em JSON assim:
{
  "action": "CHAT",
  "reply": "Sua resposta aqui"
}"""

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json or {}
    user_message = data.get('message', '')
    context = data.get('context', {})
    history_data = data.get('history', [])  # Histórico vindo do frontend

    # Monta a mensagem atual incorporando o contexto da agenda
    current_prompt = f"""[CONTEXTO DA AGENDA]
Data Hoje: {context.get('current_date')}
Tarefas Atuais: {context.get('tasks')}

[MENSAGEM DO USUÁRIO]
{user_message}"""

    # Converte o histórico recebido para os objetos types.Content da SDK
    contents = []
    for item in history_data:
        role = item.get('role')  # 'user' ou 'model'
        parts_text = item.get('parts', '')
        if role and parts_text:
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=parts_text)]
                )
            )

    # Adiciona a mensagem atual no final da lista de conteúdos
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=current_prompt)]
        )
    )

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json"
            )
        )
        return jsonify(json.loads(response.text))
    except Exception as e:
        return jsonify({"action": "CHAT", "reply": f"Erro no servidor: {str(e)}"}), 500

if __name__ == '__main__':
    print("🚀 Servidor do Aquiles rodando...")
    app.run(port=5000, debug=True)
