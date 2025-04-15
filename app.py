from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Cliente OpenAI
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Prompt base da personagem Graziela
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
    data = request.get_json()
    payload = data.get("payload", {})

    user_message = payload.get("var_480", "")

    messages = [
        {"role": "system", "content": BASE_PROMPT},
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.85,
        max_tokens=700
    )

    reply = response.choices[0].message.content.strip()

    # ✅ Retorno ideal para que a Reportana envie direto no WhatsApp
    return jsonify({
        "reply": reply
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
