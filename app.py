from flask import Flask, request, jsonify, make_response
import openai
import os
import time
from datetime import datetime

app = Flask(__name__)

# 🔐 Autenticação com a OpenAI
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 🧠 Memória dos históricos por cliente (armazenada em dicionário)
historicos = {}

# 💬 Prompt base completo da Graziela
BASE_PROMPT = """
[... mantenha aqui seu prompt completo como já está ...]
"""

@app.route("/", methods=["GET"])
def home():
    return "Servidor da Graziela com memória ativa 💬🧠"

@app.route("/webhook", methods=["POST"])
def webhook():
    start = time.time()
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # 📥 Recebe a mensagem vinda da Reportana
    data = request.get_json()
    payload = data.get("payload", {})
    combo = payload.get("var_480", "")

    # 🔍 Extrai o telefone e a mensagem do campo var_480
    try:
        telefone, mensagem = combo.split("|||", 1)
    except ValueError:
        telefone = "anonimo"
        mensagem = combo.strip()

    # 🧠 Recupera o histórico anterior do cliente
    historico = historicos.get(telefone, "")

    # 🗣️ Monta a conversa para o GPT
    messages = [{"role": "system", "content": BASE_PROMPT}]
    if historico:
        messages.append({"role": "user", "content": historico})
    messages.append({"role": "user", "content": mensagem})

    # 💬 Gera a resposta da IA
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.5,
            max_tokens=300
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = "Tivemos uma instabilidade agora, mas pode me mandar de novo? 🙏"

    # 🧠 Atualiza o histórico de conversa
    novo_historico = f"{historico}\nCliente: {mensagem}\nGraziela: {reply}".strip()
    historicos[telefone] = novo_historico

    # 📋 Log de execução
    print("\n========== [GRAZIELA LOG] ==========")
    print(f"📆 {now}")
    print(f"📱 Telefone: {telefone}")
    print(f"📩 Mensagem: {mensagem}")
    print(f"🤖 Resposta: {reply}")
    print(f"📚 Histórico:\n{novo_historico}")
    print(f"⏱️ Tempo de resposta: {round(time.time() - start, 2)} segundos")
    print("=====================================\n")

    # ✅ Retorna a resposta no formato esperado pela Reportana
    response_json = {
        "payload": {
            "resposta": reply
        }
    }

    resp = make_response(jsonify(response_json), 200)
    resp.headers["Content-Type"] = "application/json"
    return resp

# 🧪 Executa localmente apenas em modo dev
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
