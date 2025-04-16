from flask import Flask, request, jsonify, make_response
import openai
import os
import time
from datetime import datetime

app = Flask(__name__)

# 🔐 Autenticação com a OpenAI
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 💬 Prompt base com estilo humano, sem quebras de linha
BASE_PROMPT = """
Você é Graziela, vendedora da Sportech.

Fale como se estivesse conversando no WhatsApp, com tom acolhedor e humano.

Nunca responda como um robô. Converse com empatia, leveza e escuta ativa.

Escreva tudo em uma única linha, sem quebras (sem \\n).
"""

@app.route("/", methods=["GET"])
def home():
    return "Servidor da Graziela ativo 💬🧠"

@app.route("/webhook", methods=["POST"])
def webhook():
    start = time.time()
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # 📥 Recebe a mensagem do cliente da Reportana
    data = request.get_json()
    payload = data.get("payload", {})
    user_message = payload.get("var_480", "[mensagem vazia]")

    # 🤖 Monta a conversa com o GPT
    messages = [
        {"role": "system", "content": BASE_PROMPT},
        {"role": "user", "content": user_message}
    ]

    # 🧠 Chamada para o GPT
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.5,
        max_tokens=300
    )

    # 🧹 Limpa a resposta: sem quebras de linha
    reply = response.choices[0].message.content.strip()
    resposta_formatada = reply.replace("\n", " ").replace("\\n", " ").strip()

    elapsed = round(time.time() - start, 2)

    # 📋 Log para o Render
    print("\n========== [GRAZIELA LOG] ==========")
    print(f"📆 {now}")
    print(f"📩 Mensagem recebida: {user_message}")
    print(f"🤖 Resposta gerada (original): {reply}")
    print(f"💬 Resposta enviada (sem quebra): {resposta_formatada}")
    print(f"⏱️ Tempo de resposta: {elapsed} segundos")
    print("=====================================\n")

    # ✅ Retorno correto para a Reportana
    response_json = {
        "payload": {
            "resposta": resposta_formatada
        }
    }

    resp = make_response(jsonify(response_json), 200)
    resp.headers["Content-Type"] = "application/json"
    return resp

# 🧪 Executa localmente apenas em modo dev
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
