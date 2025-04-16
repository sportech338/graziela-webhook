from flask import Flask, request, jsonify, make_response
import openai
import os
import time

app = Flask(__name__)

# 🔐 Autenticação com a OpenAI (usando variável de ambiente segura)
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 💬 Prompt padrão da Graziela (vendedora empática, estilo WhatsApp)
BASE_PROMPT = """
Você é Graziela, vendedora da Sportech.

Fale como se estivesse digitando no WhatsApp, com pausas reais (\\n\\n), tom acolhedor e humano.

Nunca responda como um robô. Converse com empatia, leveza e escuta ativa.
"""

@app.route("/", methods=["GET"])
def home():
    return "Servidor da Graziela ativo 💬🧠"

@app.route("/webhook", methods=["POST"])
def webhook():
    start = time.time()

    # 📥 Recebe o JSON enviado pela Reportana
    data = request.get_json()
    payload = data.get("payload", {})
    user_message = payload.get("var_480", "")

    # 🤖 Prepara a conversa com o GPT
    messages = [
        {"role": "system", "content": BASE_PROMPT},
        {"role": "user", "content": user_message}
    ]

    # 🧠 Chamada à OpenAI com modelo GPT-4o
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.5,
        max_tokens=300
    )

    reply = response.choices[0].message.content.strip()

    elapsed = time.time() - start
    print(f"⏱️ Tempo de resposta GPT: {elapsed:.2f} segundos")
    print(f"📤 Resposta enviada: {reply}")

    # ✅ Retorno correto no formato que a Reportana espera
    response_json = {
        "payload": {
            "resposta": reply
        }
    }

    resp = make_response(jsonify(response_json), 200)
    resp.headers["Content-Type"] = "application/json"
    return resp

# ❗ Em produção, o Render usará gunicorn para iniciar este app,
# então este bloco só serve para testes locais (pode manter se quiser testar localmente)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
