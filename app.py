from flask import Flask, request, jsonify

app = Flask(__name__)

# Mensagem fixa para teste (sem uso do OpenAI ainda)
RESPOSTA_FIXA = "Oi! Tudo bem? 👋 Essa é uma resposta teste da Graziela."

@app.route("/", methods=["GET"])
def home():
    return "Servidor da Graziela ativo 💬🧠"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    payload = data.get("payload", {})

    user_message = payload.get("var_480", "")
    print("🔹 Mensagem recebida:", user_message)

    reply = RESPOSTA_FIXA  # Resposta fixa para teste

    # Retorno no formato que a Reportana espera
    return jsonify({
        "payload": {
            "var_273": reply
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
