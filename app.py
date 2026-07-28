import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)

# Busca a chave nas variáveis de ambiente do Render
api_key = os.getenv("GEMINI_API_KEY")

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
    # 1. Validação da API Key
    if not api_key:
        print("❌ ERRO: A variável GEMINI_API_KEY não foi encontrada no ambiente!")
        return jsonify({
            "action": "CHAT",
            "reply": "Erro de configuração no servidor: GEMINI_API_KEY não foi definida no Render."
        }), 500

    try:
        # Inicializa o cliente dentro do bloco seguro
        client = genai.Client(api_key=api_key)
        
        data = request.json or {}
        user_message = data.get('message', '')
        context = data.get('context', {})
        history_data = data.get('history', [])

        current_prompt = f"""[CONTEXTO DA AGENDA]
Data Hoje: {context.get('current_date', '')}
Tarefas Atuais: {context.get('tasks', [])}

[MENSAGEM DO USUÁRIO]
{user_message}"""

        # 2. Montagem segura do histórico
        contents = []
        for item in history_data:
            role = item.get('role')
            parts_val = item.get('parts') or item.get('text', '')
            
            if isinstance(parts_val, list) and len(parts_val) > 0:
                parts_text = parts_val[0]
            else:
                parts_text = str(parts_val)

            if role and parts_text:
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=parts_text)]
                    )
                )

        # Adiciona o prompt atual
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=current_prompt)]
            )
        )

        # 3. Chamada para o Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json"
            )
        )

        # Tenta interpretar o JSON retornado pela IA
        try:
            res_json = json.loads(response.text)
            return jsonify(res_json)
        except json.JSONDecodeError:
            return jsonify({
                "action": "CHAT",
                "reply": response.text
            })

    except Exception as e:
        print(f"❌ ERRO NO PROCESSAMENTO DA REQUISIÇÃO: {str(e)}")
        return jsonify({
            "action": "CHAT",
            "reply": f"Erro interno no Python: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
