from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Servidor da Graziela ativo 💬🧠"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📩 Dados recebidos:", data)

    return jsonify({
        "var_273": "🧪 Teste direto: webhook respondeu com sucesso!"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
