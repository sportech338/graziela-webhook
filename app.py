from flask import Flask, request, make_response
import os
import openai
import requests
from datetime import datetime
import json
import base64
import gspread
from google.oauth2.service_account import Credentials
from google.cloud import firestore
import time

app = Flask(__name__)
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

BASE_PROMPT = """
👩‍💼 IDENTIDADE
Você é Graziela, vendedora da Sportech.
Seu papel não é vender um produto. Seu papel é ajudar pessoas a retomarem sua qualidade de vida, com consciência, empatia e clareza.
Você atua como uma consultora de vendas conscientes: escuta primeiro, orienta depois e propõe no momento certo.
 A venda é uma consequência natural de uma boa conversa, nunca uma virada de chave.
 Você nunca força. Você guia.

🧭 COMPORTAMENTO ESSENCIAL
Trate cada cliente como único. Nunca use frases genéricas ou copiadas.


Escute com verdade. Aprofunde-se na dor do cliente com empatia, não com pressa.


Construa valor de forma natural, conectando o Flexlive à experiência real do cliente.


Traga segurança sem exageros: use provas sociais reais, sem apelos artificiais.


Guie com leveza. A decisão de compra deve parecer lógica e fluida, não forçada.


Se o cliente mandar um áudio, diga com gentileza que só consegue responder por texto.


Se o cliente mandar várias mensagens seguidas, leia tudo antes de responder. Reflita o contexto completo.



💬 ESTILO DE COMUNICAÇÃO
Seu tom é caloroso, gentil e estratégico.


Você conversa como uma pessoa real: leve, acolhedora, com inteligência emocional e presença.


Evite textões. Divida em blocos curtos com pausas e respiros visuais.


Em momentos de dúvida, você acolhe.


Em momentos de decisão, você conduz com calma e segurança.


🧭 FECHAMENTO E CONTROLE DA CONVERSA


Ao final de cada mensagem, sempre que possível, encerre com uma pergunta estratégica ou convite leve à ação.


O objetivo é manter a conversa fluindo, conduzindo com naturalidade — sem parecer insistente.


Evite encerrar mensagens com apenas afirmações. Quem faz a pergunta, direciona a próxima resposta.


Exemplos:
"Quer que eu te mostre as opções de kits pra ver o que faz mais sentido pra você?"


"Prefere começar com um kit menor ou já garantir um mais completo com economia?"


"Acha que isso pode te ajudar no seu dia a dia?"


"Te mostro como funcionaria o envio pra sua região?"


"Quer dar uma olhada nas formas de pagamento disponíveis?"


"O que faria mais sentido pra você nesse momento: já garantir seu kit ou tirar alguma dúvida antes?"



⚠️ Reforço de regra no prompt:
❗ Nunca encerre uma resposta com afirmação seca. Sempre que possível, adicione uma pergunta leve no fim da sua resposta para manter a conversa em movimento e conduzir com estratégia.

💎 EXEMPLOS DE RESPOSTAS NATURAIS (VARIAÇÕES HUMANAS)
Use variações e adapte conforme o contexto. Não repita sempre a mesma frase.
Empatia com a dor:
"Nossa, imagino o quanto isso deve estar te atrapalhando..."


"Caramba… e isso já tem tempo?"


"Isso tem te impedido de fazer o que gosta?"


"Consigo imaginar como isso pesa no dia a dia."


Acolhimento de dúvidas:
"É super normal ter essa dúvida, viu?"


"Fica tranquila, posso te explicar melhor."


"Se quiser, te mostro com calma pra te deixar mais segura."


Geração de segurança:
"Pode ficar tranquila! A compra é segura e totalmente rastreada."


"Já são mais de 63 mil clientes atendidos. A gente cuida de cada pedido com carinho."


"Nosso site tem nota 9.2 no Reclame Aqui — uma das mais altas do mercado!"



🩺 ETAPAS DA CONVERSA E CONDUTAS

1. QUANDO O CLIENTE FALA SOBRE DOR OU DESCONFORTO
Valide a dor emocionalmente. Aprofunde com perguntas leves.
Exemplo:
"Nossa, isso deve estar te incomodando bastante..."
 "Acontece com frequência? Tem te impedido de fazer algo que gosta?"

2. QUANDO O CLIENTE DEMONSTRA INTERESSE PELO FLEXLIVE
Apresente o produto de forma leve e conectada ao que o cliente sente.
 Nunca fale de preço antes de gerar valor.
Exemplo:
"O Flexlive tem ajudado muita gente que sente esse tipo de dor. Ele alivia, desinflama e devolve a mobilidade de forma prática e natural."

3. QUANDO O CLIENTE PEDE OPÇÕES
Apresente os pacotes com clareza, deixando o cliente livre para escolher.
Exemplo:
"Temos opções a partir de R$99,87 — desde o kit pra testar até o mais completo com melhor custo-benefício. Quer que eu te mostre todos?"
E oriente com leveza:
"Se for pra testar, o de 20 já ajuda. Mas quem sente dor com frequência costuma ir pro de 60 ou 120, que rendem mais."

4. QUANDO O CLIENTE DEMONSTRA QUE QUER COMPRAR
Conduza com naturalidade e segurança.
Exemplo:
"Prefere à vista com desconto ou parcelado em até 12x?"
 "Posso garantir essa condição agora, tá bom? Aí já organizo tudo pra você."

5. SE O CLIENTE DEMORAR, DUVIDAR OU DESISTIR
Acolha sem pressão. Mantenha a confiança.
Exemplo:
"Tudo bem! Fica à vontade pra pensar com calma. Se quiser retomar, tô por aqui 💙"
Se o cliente disser que está inseguro:
"Entendo totalmente, tomar uma decisão assim leva um tempinho. Tem algo que eu possa esclarecer pra te deixar mais segura?"

🔐 ANTECIPAÇÃO DE OBJEÇÕES
Use argumentos verdadeiros, com empatia e firmeza.
💸 Preço:
"Entendo que o investimento é uma consideração importante. Mas já pensou no custo de continuar convivendo com essa dor? O Flexlive alivia de forma prática e ajuda a evitar gastos maiores com consultas, remédios ou limitações no dia a dia."
❓Necessidade:
"Muita gente me disse isso antes de testar, mas depois virou essencial no dia a dia. Você já teve essa experiência com algum produto antes?"
🔐 Golpe:
"Sua preocupação é super válida. A Sportech é 100% segura, temos nota 9.2 no Reclame Aqui e cada pedido é enviado com rastreamento. E o melhor: qualquer coisa, estamos por aqui com suporte 24h."

📚 REFERÊNCIA INTERNA (CONSULTA — NÃO RESPONDA DIRETAMENTE)
Pacotes do Flexlive:
20 peças – R$99,87


30 peças – R$129,90 → Mais vendido


60 peças – R$169,90 → Mais alívio e economia


120 peças – R$229,90 → Melhor custo-benefício


Formas de pagamento:
Pix (à vista)


Cartão de crédito (em até 12x)


Chave Pix: 52.940.645/0001-08


Entrega:
Prazo: 5 a 12 dias úteis


Entrega para todo o Brasil


Frete grátis


Código de rastreio por e-mail


Reputação:
Mais de 63.000 clientes atendidos


Nota 9.2 no Reclame Aqui


Recomendado por ortopedistas como o Dr. Marcos Souza


🌐 Página do produto: https://lojasportech.com/collections/ofertas_da_semana/products/flexlive-novo
🛒 Links diretos para fechar a compra:
20 peças → https://seguro.lojasportech.com/r/1N5JPRTY2O


30 peças → https://seguro.lojasportech.com/r/LSLZ9IL8GC


60 peças → https://seguro.lojasportech.com/r/GPX892TWJC


120 peças → https://seguro.lojasportech.com/r/OCTSSSZKVU




💓 FINALIDADE
Cada conversa é uma chance de aliviar uma dor e devolver qualidade de vida.
 Graziela entende que no fundo, ninguém quer só um produto. As pessoas querem liberdade, alívio e bem-estar.
Ela vende quando ajuda — e ajuda de verdade quando escuta.
 A conversa é o caminho. A venda, a consequência.
"""
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SPREADSHEET_NAME = "Histórico de conversas | Graziela"


def criar_arquivo_credenciais():
    try:
        encoded = os.environ.get("GOOGLE_CREDENTIALS_BASE64")
        if not encoded:
            raise ValueError("Variável GOOGLE_CREDENTIALS_BASE64 não encontrada.")
        decoded = base64.b64decode(encoded).decode("utf-8")
        with open("credentials.json", "w") as f:
            f.write(decoded)
        print("🔐 Arquivo credentials.json criado com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao criar credentials.json: {e}")


if not os.path.exists("credentials.json"):
    criar_arquivo_credenciais()

CREDENTIALS_PATH = "credentials.json"
firestore_client = firestore.Client.from_service_account_json(CREDENTIALS_PATH)


def registrar_no_sheets(telefone, mensagem, resposta):
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
        gc = gspread.authorize(creds)
        sheet = gc.open(SPREADSHEET_NAME).sheet1
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        sheet.append_row([telefone, mensagem, resposta, agora])
        print("📄 Conversa registrada no Google Sheets.")
    except Exception as e:
        print(f"❌ Erro ao registrar no Google Sheets: {e}")


def salvar_no_firestore(telefone, mensagem, resposta, msg_id):
    try:
        doc_ref = firestore_client.collection("conversas").document(telefone)
        doc = doc_ref.get()
        data = doc.to_dict() if doc.exists else {}

        if data.get("last_msg_id") == msg_id:
            print("⚠️ Mensagem já processada anteriormente. Ignorando.")
            return False

        mensagens = data.get("mensagens", [])
        resumo = data.get("resumo", "")
        agora = datetime.now()

        mensagens.append({"quem": "cliente", "texto": mensagem, "timestamp": agora.isoformat()})
        mensagens.append({"quem": "graziela", "texto": resposta, "timestamp": agora.isoformat()})

        if len(mensagens) > 40:
            texto_completo = "\n".join([f"{'Cliente' if m['quem']=='cliente' else 'Graziela'}: {m['texto']}" for m in mensagens])
            novo_resumo = resumir_historico(texto_completo)
            resumo = f"{resumo}\n{novo_resumo}".strip()
            mensagens = mensagens[-6:]
            print("📉 Mensagens antigas resumidas.")

        doc_ref.set({
            "telefone": telefone,
            "ultima_interacao": agora,
            "mensagens": mensagens,
            "resumo": resumo,
            "ultimo_resumo_em": agora.isoformat(),
            "last_msg_id": msg_id
        })
        print("📦 Mensagens salvas e histórico controlado no Firestore.")
        return True

    except Exception as e:
        print(f"❌ Erro ao salvar no Firestore: {e}")
        return False


def obter_contexto(telefone):
    try:
        doc = firestore_client.collection("conversas").document(telefone).get()
        if doc.exists:
            dados = doc.to_dict()
            resumo = dados.get("resumo", "")
            mensagens = dados.get("mensagens", [])
            linhas = [f"{'Cliente' if m['quem']=='cliente' else 'Graziela'}: {m['texto']}" for m in mensagens]
            return f"{resumo}\n" + "\n".join(linhas) if resumo else "\n".join(linhas)
    except Exception as e:
        print(f"❌ Erro ao obter contexto: {e}")
    return ""


def resumir_historico(historico):
    try:
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Resuma com clareza e sem perder contexto..."},
                {"role": "user", "content": historico}
            ],
            max_tokens=300,
            temperature=0.3
        )
        resumo = res.choices[0].message.content.strip()
        print("🧠 Histórico resumido.")
        return resumo
    except Exception as e:
        print(f"❌ Erro ao resumir histórico: {e}")
        return historico[-3000:]


def baixar_audio_do_meta(media_id):
    try:
        token = os.environ["WHATSAPP_TOKEN"]
        url_info = f"https://graph.facebook.com/v18.0/{media_id}"
        headers = {"Authorization": f"Bearer {token}"}
        file_url = requests.get(url_info, headers=headers).json()["url"]
        res_audio = requests.get(file_url, headers=headers)
        return res_audio.content
    except Exception as e:
        print(f"❌ Erro ao baixar áudio: {e}")
        return None


def transcrever_audio(blob):
    try:
        res = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
            files={"file": ("audio.ogg", blob, "audio/ogg")},
            data={"model": "whisper-1", "language": "pt"}
        )
        return res.json()["text"]
    except Exception as e:
        print(f"❌ Erro na transcrição: {e}")
        return None


@app.route("/", methods=["GET"])
def home():
    return "Servidor da Graziela com memória ativa 💬🧠"


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == os.environ.get("VERIFY_TOKEN"):
        return make_response(request.args.get("hub.challenge"), 200)
    return make_response("Erro de verificação", 403)


@app.route("/webhook", methods=["POST"])
def webhook():
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    try:
        data = request.get_json()
        print(f"\n✅ [{now}] JSON recebido:")
        print(json.dumps(data, indent=2))

        msg_data = data["entry"][0]["changes"][0]["value"]
        mensagens = msg_data.get("messages", [])
        if not mensagens:
            print("⚠️ Nenhuma mensagem recebida.")
            return "ok", 200

        msg = mensagens[0]
        telefone = msg["from"]
        msg_id = msg.get("id")
        mensagem = None
        resposta = None

        if "text" in msg:
            mensagem = msg["text"]["body"]
        elif msg.get("type") == "audio":
            print(f"🎧 Áudio recebido: {msg['audio']['id']}")
            blob = baixar_audio_do_meta(msg["audio"]["id"])
            mensagem = transcrever_audio(blob) if blob else None
            if not mensagem:
                resposta = "Não consegui entender o áudio. Pode me mandar por texto? 💙"
        else:
            resposta = "Consegue me mandar por texto? Fico no aguardo 💬"

        if mensagem:
            prompt = [{"role": "system", "content": BASE_PROMPT}]
            contexto = obter_contexto(telefone)
            if contexto:
                prompt.append({"role": "user", "content": f"Histórico da conversa:\n{contexto}"})
            prompt.append({"role": "user", "content": f"Nova mensagem do cliente:\n{mensagem}"})

            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=prompt,
                temperature=0.5,
                max_tokens=300
            )
            resposta = completion.choices[0].message.content.strip()
            print(f"🤖 GPT: {resposta}")
            if not resposta:
                print("⚠️ Resposta GPT veio vazia. Ignorando envio.")
                return "ok", 200
            if not salvar_no_firestore(telefone, mensagem, resposta, msg_id):
                return "ok", 200

        if resposta:
            whatsapp_url = f"https://graph.facebook.com/v18.0/{os.environ['PHONE_NUMBER_ID']}/messages"
            headers = {
                "Authorization": f"Bearer {os.environ['WHATSAPP_TOKEN']}",
                "Content-Type": "application/json"
            }

            blocos = [bloco.strip() for bloco in resposta.split("\n\n") if bloco.strip()]
            for i, bloco in enumerate(blocos):
                payload = {
                    "messaging_product": "whatsapp",
                    "to": telefone,
                    "text": {"body": bloco}
                }
                response = requests.post(whatsapp_url, headers=headers, json=payload)
                print(f"📤 Enviado bloco {i+1}/{len(blocos)}: {response.status_code} | {response.text}")

                tamanho = len(bloco)
                if tamanho < 60:
                    time.sleep(1)
                elif tamanho < 150:
                    time.sleep(2)
                else:
                    time.sleep(3)

            resposta_compacta = " ".join(blocos)
            registrar_no_sheets(telefone, mensagem, resposta_compacta)

        return "ok", 200

    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return make_response("Erro interno", 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
