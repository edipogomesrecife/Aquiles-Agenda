import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)  # Permite que o index.html converse com o Python

# Configure sua API Key do Gemini aqui
client = genai.Client(api_key="AQ.Ab8RN6K5kPO6QuarGFKsXo8Ec4ZTOrjfsv2t2xQhQbSVjZcDxw")

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
    
    prompt = f"""[CONTEXTO DA AGENDA]
Data Hoje: {context.get('current_date')}
Tarefas Atuais: {context.get('tasks')}

[MENSAGEM DO USUÁRIO]
{user_message}"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json"
            )
        )
        return jsonify(json.loads(response.text))
    except Exception as e:
        return jsonify({"action": "CHAT", "reply": f"Erro no servidor: {str(e)}"}), 500

if __name__ == '__main__':
    print("🚀 Servidor do Aquiles rodando em http://localhost:5000")
    app.run(port=5000, debug=True)