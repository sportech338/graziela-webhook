from flask import Flask, request, jsonify, make_response
import openai
import os
import time
from datetime import datetime
import requests
from io import BytesIO

app = Flask(__name__)

# 🔐 Autenticação com a OpenAI
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 🧠 Memória dos históricos por cliente
historicos = {}

# 💬 Prompt base da Graziela
BASE_PROMPT = """
Você é Graziela, vendedora da Sportech. Seu papel não é vender um produto. Seu papel é ajudar pessoas a retomarem sua qualidade de vida com consciência, empatia e clareza.

Você conversa como uma pessoa real: leve, acolhedora, com inteligência emocional e presença.  
Seu tom é humano. Sua escuta é ativa. Suas respostas são guiadas com intenção.

A venda acontece como um desfecho natural de uma conversa boa — não como uma virada de chave. Você nunca força. Você guia.

🧠 COMPORTAMENTO ESSENCIAL

Trate cada cliente como único. Nunca use frases genéricas ou copiadas.

Escute de verdade. Aprofunde-se na dor do cliente com empatia, não com pressa.

Construa valor com naturalidade, conectando o Flexlive com o que o cliente está vivendo.

Traga segurança sem exagerar: use provas sociais reais, sem apelos artificiais.

Guie com leveza. A decisão de comprar deve parecer lógica e fluida, não forçada.

Se o cliente mandar um áudio, diga com gentileza que só consegue responder por texto.

Se o cliente mandar várias mensagens seguidas, leia tudo antes de responder. Reflita o contexto completo.

💬 COMO VOCÊ SE COMUNICA

Seu tom é caloroso, gentil e estratégico.
Você faz pausas entre blocos. Nunca envia textões.

Em momentos de dúvida, você acolhe. Em momentos de decisão, você conduz com calma.

📦 Pacotes do Flexlive:
- 20 unidades – R$99,87 → Ideal pra testar
- 45 unidades – R$139,90 → Econômico
- 60 unidades – R$149,90 → Mais vendido
- 120 unidades – R$199,90 → Melhor custo-benefício

💰 Formas de pagamento:
- Pix (à vista) — CNPJ: 52940645000108
- Cartão de crédito (até 12x)

🚚 Entrega:
- Prazo: 5 a 12 dias úteis
- Frete grátis para todo o Brasil

⭐ Reputação:
- 63.000 clientes atendidos
- Nota 8.9 no Reclame Aqui
- Recomendado por ortopedistas (Dr. Marcos Souza)

🌐 Produto: https://lojasportech.com/collections/ofertas_da_semana/products/flexlive-novo
🛒 Fechamento:
- 20 peças → https://seguro.lojasportech.com/r/1N5JPRTY2O
- 45 peças → https://seguro.lojasportech.com/r/927Q2G8120
- 60 peças → https://seguro.lojasportech.com/r/GPX892TWJC
- 120 peças → https://seguro.lojasportech.com/r/OCTSSSZKVU
"""

@app.route("/", methods=["GET"])
def home():
    return "Servidor da Graziela com memória ativa 💬🧠"

@app.route("/webhook", methods=["POST"])
def webhook():
    start = time.time()
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    data = request.get_json() or {}
    payload = data.get("payload") or {}
    mensagem_raw = (payload.get("var_480") or "").strip()
    telefone = (data.get("customer", {}) or {}).get("phone", "anonimo").strip()

    print("🔎 JSON completo recebido:", data)
    print("📱 Telefone identificado:", telefone)
    print("💬 Mensagem recebida:", mensagem_raw)

    # 🎧 Detecta se é áudio no formato "áudio|||<link>"
    if "|||" in mensagem_raw:
        tipo, audio_url = mensagem_raw.split("|||", 1)
        if tipo.strip().lower() in ["áudio", "audio"]:
            try:
                print(f"🎵 URL do áudio detectada: {audio_url}")
                audio_response = requests.get(audio_url)
                audio_bytes = BytesIO(audio_response.content)

                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=("audio.ogg", audio_bytes, "audio/ogg"),
                    response_format="text"
                )
                mensagem = transcript.strip()
            except Exception as e:
                print(f"❌ Erro ao transcrever: {e}")
                mensagem = "Ah, eu não consigo ouvir áudios, mas posso te ajudar por texto! Me conta o que você precisa 😊"
        else:
            mensagem = mensagem_raw
    else:
        mensagem = mensagem_raw

    # 🧠 Verifica se é a primeira mensagem e se veio de áudio
    historico = historicos.get(telefone, "")
    primeiro_contato = not historico.strip()
    veio_de_audio = mensagem_raw.lower().startswith("audio|||") or mensagem_raw.lower().startswith("áudio|||")

    if primeiro_contato and veio_de_audio:
        reply = (
            "Acabei de ouvir aqui 🌟\n\n"
            "Pode me contar um pouquinho melhor o que está acontecendo? "
            "Tô aqui pra te ajudar do jeitinho certo 😊"
        )
        historicos[telefone] = f"Cliente: {mensagem}\nGraziela: {reply}".strip()

        print("\n========== [GRAZIELA LOG - ÁUDIO INICIAL] ==========")
        print(f"📆 {now}")
        print(f"📱 Telefone: {telefone}")
        print(f"📩 Mensagem (transcrita): {mensagem}")
        print(f"🤖 Resposta: {reply}")
        print("=====================================================\n")

        return make_response(jsonify({"payload": {"resposta": reply}}), 200)

    # ✨ Atendimento normal com histórico
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

    historicos[telefone] = f"{historico}\nCliente: {mensagem}\nGraziela: {reply}".strip()

    print("\n========== [GRAZIELA LOG] ==========")
    print(f"📆 {now}")
    print(f"📱 Telefone: {telefone}")
    print(f"📩 Mensagem: {mensagem}")
    print(f"🤖 Resposta: {reply}")
    print(f"📚 Histórico:\n{historicos[telefone]}")
    print(f"⏱️ Tempo de resposta: {round(time.time() - start, 2)} segundos")
    print("=====================================\n")

    return make_response(jsonify({"payload": {"resposta": reply}}), 200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
