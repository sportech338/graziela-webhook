from flask import Flask, request, jsonify, make_response
import openai
import os
import time

app = Flask(__name__)

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

BASE_PROMPT = """
Você é Graziela, vendedora da Sportech.

Fale como se estivesse digitando no WhatsApp, com pausas reais (\\n\\n), tom acolhedor e humano.

Nunca responda como um robô. Converse com empatia, leveza e escuta ativa.
"""

@app.route("/webhook", methods=["POST"])
def webhook():
    start = time.time()

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
        temperature=0.5,
        max_tokens=300
    )

    reply = response.choices[0].message.content.strip()

    elapsed = time.time() - start
    print(f"⏱️ Tempo de resposta GPT: {elapsed:.2f} segundos")
    print(f"📤 Resposta enviada: {reply}")

    # Força o retorno como JSON válido
    resp = make_response(jsonify({
        "payload": {
            "var_273": reply
        }
    }))
    resp.headers["Content-Type"] = "application/json"
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
