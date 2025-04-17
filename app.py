from flask import Flask, request, jsonify, make_response
import openai
import os
import time
from datetime import datetime
import json

app = Flask(__name__)

# 🔐 Autenticação com a OpenAI
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 🧠 Memória dos históricos por cliente
historicos = {}

# 💬 Prompt base (resumido para teste)
BASE_PROMPT = """
Você é Graziela, vendedora da Sportech. Seu papel é ajudar pessoas com empatia e orientação clara. Sempre responda com acolhimento, pausas naturais e foco humano.
"""

@app.route("/", methods=["GET"])
def home():
    return "Servidor da Graziela com memória ativa 💬🧠"

@app.route("/webhook", methods=["POST"])
def webhook():
    start = time.time()
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    try:
        data = request.get_json(force=True)
    except Exception as e:
        print("❌ Erro ao tentar decodificar JSON:", e)
        data = {}

    print("\n========= 🌐 JSON COMPLETO RECEBIDO =========")
    print(data)
    print("=============================================\n")

    payload = data.get("payload", {})
    print("📦 Payload recebido:", payload)

    # 🧾 Pega o conteúdo enviado da Reportana — agora usando {{ message }} em resposta
    resposta_payload = payload.get("resposta")
    mensagem = ""

    if isinstance(resposta_payload, str):
        conteudo = resposta_payload.strip()
        try:
            parsed = json.loads(conteudo)
            if isinstance(parsed, dict):
                tipo = parsed.get("type", "desconhecido")
                mensagem = f"[mensagem estruturada recebida: {tipo}]"
                print("📎 resposta.payload como JSON estruturado:", parsed)
            else:
                mensagem = conteudo
        except json.JSONDecodeError:
            mensagem = conteudo
    elif isinstance(resposta_payload, dict):
        tipo = resposta_payload.get("type", "desconhecido")
        mensagem = f"[mensagem estruturada recebida: {tipo}]"
        print("📎 resposta.payload como dict:", resposta_payload)
    else:
        mensagem = "[mensagem vazia ou não reconhecida]"

    telefone = data.get("customer", {}).get("phone", "anonimo").strip()
    print("📱 Telefone identificado:", telefone)
    print("💬 Mensagem recebida:", mensagem)

    historico = historicos.get(telefone, "")
    messages = [{"role": "system", "content": BASE_PROMPT}]
    if historico:
        messages.append({"role": "user", "content": historico})
    messages.append({"role": "user", "content": mensagem})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.5,
            max_tokens=300
        )
        reply = response.choices[0].message.content.strip()
    except Exception:
        reply = "Tivemos uma instabilidade agora, mas pode me mandar de novo? 🙏"

    novo_historico = f"{historico}\nCliente: {mensagem}\nGraziela: {reply}".strip()
    historicos[telefone] = novo_historico

    print("\n========== [GRAZIELA LOG] ==========")
    print(f"🗖️ {now}")
    print(f"📱 Telefone: {telefone}")
    print(f"📩 Mensagem: {mensagem}")
    print(f"🤖 Resposta: {reply}")
    print(f"📚 Histórico:\n{novo_historico}")
    print(f"⏱️ Tempo de resposta: {round(time.time() - start, 2)} segundos")
    print("=====================================\n")

    response_json = {
        "payload": {
            "resposta": reply
        }
    }

    resp = make_response(jsonify(response_json), 200)
    resp.headers["Content-Type"] = "application/json"
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
