from flask import Flask, request, jsonify, make_response
import openai
import os
import time
from datetime import datetime

app = Flask(__name__)

# 🔐 Autenticação com a OpenAI
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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

Esse é o espírito da Graziela: presença, sensibilidade e intenção.  
Ela vende quando ajuda — e ajuda de verdade quando escuta. A conversa é o caminho. A venda, a consequência.
"""

@app.route("/", methods=["GET"])
def home():
    return "Servidor da Graziela ativo 💬🧠"

@app.route("/webhook", methods=["POST"])
def webhook():
    start = time.time()
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # 📥 Recebe o JSON da Reportana com a mensagem do cliente
    data = request.get_json()
    payload = data.get("payload", {})
    user_message = payload.get("var_480", "[mensagem vazia]")

    # 🤖 Monta a conversa com o GPT-4o
    messages = [
        {"role": "system", "content": BASE_PROMPT},
        {"role": "user", "content": user_message}
    ]

    # 🧠 Gera a resposta da IA
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.5,
        max_tokens=300
    )

    reply = response.choices[0].message.content.strip()
    elapsed = round(time.time() - start, 2)

    # 📋 Log da conversa no terminal (Render)
    print("\n========== [GRAZIELA LOG] ==========")
    print(f"📆 {now}")
    print(f"📩 Mensagem recebida: {user_message}")
    print(f"🤖 Resposta gerada: {reply}")
    print(f"⏱️ Tempo de resposta: {elapsed} segundos")
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
