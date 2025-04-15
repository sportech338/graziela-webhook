from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")

BASE_PROMPT = """
Você é Graziela, vendedora da Sportech.

Fale como se estivesse digitando no WhatsApp, com pausas reais (\n\n), tom acolhedor e humano.

Nunca responda como um robô. Converse com empatia, leveza e escuta ativa.
"""

@app.route("/", methods=["GET"])
def home():
    return "Servidor da Graziela ativo 💬🧠"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        phone = data.get("phone", "")

        messages = [
            {"role": "system", "content": BASE_PROMPT},
            {"role": "user", "content": user_message}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.85,
            max_tokens=700
        )

        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})

    except Exception as e:
        print("❌ ERRO NO WEBHOOK:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
