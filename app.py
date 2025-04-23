from flask import Flask, request, jsonify, make_response
import openai
import os
import time
from datetime import datetime
import requests
from io import BytesIO
import json

app = Flask(__name__)

# 🔐 Autenticação com a OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")

# 🧠 Memória dos históricos por cliente
historicos = {}

# 💬 Prompt base completo da Graziela
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

💎 QUANDO O CLIENTE FALA SOBRE DOR OU DESCONFORTO

Você valida emocionalmente, com empatia verdadeira. Exemplo:

"Nossa, imagino o quanto isso deve estar te atrapalhando..."

E então pergunta com calma:

"Isso acontece com frequência? Tem te impedido de fazer algo que gosta?"

🩺 QUANDO O CLIENTE DEMONSTRA INTERESSE PELO FLEXLIVE

Você responde de forma leve e personalizada, sempre conectando com o que o cliente sente:

"O Flexlive tem ajudado muita gente que sente esse tipo de dor. Ele alivia, desinflama e devolve a mobilidade, de forma prática e natural."

Você nunca apresenta os pacotes antes de validar o interesse e construir confiança.

📦 QUANDO O CLIENTE PEDE OPÇÕES

Você apresenta os kits com clareza, mas deixa o cliente livre para escolher:

"Temos opções a partir de R$99,87 — desde o kit pra testar até o mais completo com melhor custo-benefício. Quer que eu te mostre todos?"

Você orienta, mas não pressiona. Exemplo:

"Se for pra testar, o de 20 já ajuda. Mas quem sente dor com frequência costuma ir pro de 60 ou 120, que rende mais."

💰 QUANDO O CLIENTE DEMONSTRA QUE QUER COMPRAR

Você pergunta com leveza:

"Prefere à vista com desconto ou parcelado em até 12x?"

E conduz o fechamento com segurança:

"Posso garantir essa condição agora, tá bom? Aí já organizo tudo pra você."

🔁 CASO O CLIENTE DEMORE, DUVIDE OU DESISTA

Você responde com acolhimento:

"Tudo bem! Fica à vontade pra pensar com calma. Se quiser retomar, tô por aqui 💙"

📚 REFERÊNCIA INTERNA — NÃO RESPONDA ISSO DIRETAMENTE, APENAS CONSULTE SE FOR RELEVANTE NA CONVERSA:

📦 Pacotes do Flexlive:
- 20 unidades – R$99,87 → Ideal pra testar
- 45 unidades – R$139,90 → Econômico
- 60 unidades – R$149,90 → Mais vendido
- 120 unidades – R$199,90 → Melhor custo-benefício

💰 Formas de pagamento:
- Pix (à vista)
- Cartão de crédito (em até 12x)

🔐 Chave Pix:  
CNPJ: 52940645000108

🚚 Entrega:
- Prazo médio: 5 a 12 dias úteis após confirmação do pagamento
- Entrega para todo o Brasil
- Frete grátis para todas as regiões

⭐ Reputação:
- Mais de 63.000 clientes atendidos
- Nota 8.9 no Reclame Aqui
- Recomendado por ortopedistas, como o Dr. Marcos Souza

🌐 Página do produto:  
https://lojasportech.com/collections/ofertas_da_semana/products/flexlive-novo

🛒 Links diretos para fechar a compra:
- 20 peças → https://seguro.lojasportech.com/r/1N5JPRTY2O  
- 45 peças → https://seguro.lojasportech.com/r/927Q2G8120  
- 60 peças → https://seguro.lojasportech.com/r/GPX892TWJC  
- 120 peças → https://seguro.lojasportech.com/r/OCTSSSZKVU

Esse é o espírito da Graziela: presença, sensibilidade e intenção.  
Ela vende quando ajuda — e ajuda de verdade quando escuta. A conversa é o caminho. A venda, a consequência.
"""

@app.route("/", methods=["GET"])
def home():
    return "Servidor da Graziela com memória ativa 💬🧠"

# ✅ Verificação de Webhook (GET)
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == os.environ.get("VERIFY_TOKEN", "sportech-token"):
        print("🔐 Webhook verificado com sucesso!")
        return make_response(challenge, 200)
    else:
        print("❌ Verificação do webhook falhou")
        return make_response("Erro de verificação", 403)

# ✅ Recebimento de mensagens e eventos (POST)
@app.route("/webhook", methods=["POST"])
def webhook():
    start = time.time()
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    try:
        data = request.get_json() or {}
        print("\n✅ JSON recebido com sucesso")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"❌ Erro ao receber JSON: {e}")
        return make_response(jsonify({"payload": {"resposta": "Erro ao processar os dados."}}), 400)

    mensagem = ""
    telefone = "anonimo"
    GRAPH_API_VERSION = os.environ.get("GRAPH_API_VERSION", "v22.0")

    if "entry" in data:
        try:
            entry = data.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])
            statuses = value.get("statuses", [])

            # 📦 Eventos de status (entrega, leitura etc)
            if statuses:
                for status in statuses:
                    status_type = status.get("status")
                    msg_id = status.get("id")
                    recipient_id = status.get("recipient_id")
                    timestamp = status.get("timestamp")
                    print(f"📦 Evento de status: {status_type} | ID: {msg_id} | Para: {recipient_id} | ⏰ Timestamp: {timestamp}")
                return make_response("Evento de status processado com sucesso", 200)

            if not messages:
                print("⚠️ Nenhuma mensagem recebida no JSON.")
                return make_response(jsonify({"payload": {"resposta": "Mensagem vazia recebida."}}), 200)

            message = messages[0]
            telefone = message.get("from", "anonimo")
            msg_type = message.get("type")
            print(f"📲 Tipo da mensagem: {msg_type}")

            if msg_type == "text":
                mensagem = message["text"]["body"]

            elif msg_type == "audio":
                print("🎧 Mensagem de áudio recebida")
                audio_id = message["audio"]["id"]
                token = os.environ.get("WHATSAPP_API_TOKEN")
                headers = {"Authorization": f"Bearer {token}"}
                url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{audio_id}"
                print(f"🔗 Buscando URL do áudio: {url}")
                res = requests.get(url, headers=headers).json()
                audio_url = res.get("url")
                print(f"🎯 URL do áudio gerada: {audio_url}")
                audio_data = requests.get(audio_url, headers=headers)

                if audio_data.status_code == 200:
                    audio_bytes = BytesIO(audio_data.content)
                    transcript = openai.Audio.transcribe(
                        model="whisper-1",
                        file=audio_bytes
                    )
                    mensagem = transcript["text"].strip()
                    print(f"📝 Transcrição: {mensagem}")
                else:
                    mensagem = "Não consegui acessar seu áudio. Pode me contar por mensagem? 😊"

        except Exception as e:
            print(f"❌ Erro ao processar mensagem da API Meta: {e}")
            mensagem = "Desculpa, não consegui processar sua mensagem agora. Pode tentar de novo? 🙏"

    else:
        return make_response(jsonify({"payload": {"resposta": "Evento não reconhecido."}}), 400)

    # 🧠 Consulta ao GPT
    print("📚 Recuperando histórico do cliente")
    historico = historicos.get(telefone, "")
    messages = [{"role": "system", "content": BASE_PROMPT}]
    if historico:
        messages.append({"role": "user", "content": historico})
    messages.append({"role": "user", "content": mensagem})

    try:
        print("🧠 Chamando o GPT...")
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.5,
            max_tokens=300
        )
        reply = response["choices"][0]["message"]["content"].strip()
        print("🤖 Resposta do GPT recebida com sucesso")
    except Exception as e:
        print(f"❌ Erro ao chamar o GPT: {e}")
        reply = "Tivemos uma instabilidade agora, mas pode me mandar de novo? 🙏"

    historicos[telefone] = f"{historico}\nCliente: {mensagem}\nGraziela: {reply}".strip()

    print("\n========== [GRAZIELA LOG] ==========")
    print(f"📆 {now}")
    print(f"📱 Telefone: {telefone}")
    print(f"📩 Mensagem: {mensagem}")
    print(f"🤖 Resposta: {reply}")
    print("=====================================\n")

    return make_response(jsonify({"payload": {"resposta": reply}}), 200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
