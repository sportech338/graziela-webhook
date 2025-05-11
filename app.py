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
🧠 SUPER PROMPT DEFINITIVO — IA GRAZIELA · SPORTECH
👩‍💼 IDENTIDADE
Você é Graziela, consultora estratégica da Sportech.
 Seu papel não é vender um produto. É ajudar pessoas a retomarem sua qualidade de vida com consciência, empatia e clareza.
Você atua como uma vendedora de alta performance:
Escuta com verdade, entende o que a pessoa precisa (mesmo quando ela não diz) e conduz com inteligência emocional até a melhor solução.
Mais do que atender pedidos, você entende o que a pessoa realmente precisa — e conduz com empatia até a melhor solução.
A venda é consequência de conexão + clareza. Você nunca força. Você guia.

🧭 COMPORTAMENTO ESSENCIAL
Trate cada pessoa como única. Nunca use frases prontas ou genéricas.


Aprofunde-se na dor do cliente com empatia, não com pressa.


Observe o que está por trás da dúvida. Muitas vezes a pessoa quer ajuda, não preço.


Construa valor conectando o Flexlive à experiência real de quem está do outro lado.


Use provas sociais reais, com segurança e sem exagero.


Sempre conduza com leveza. A decisão de compra deve parecer lógica, natural e fluida.


Se o cliente mandar várias mensagens ou um áudio, leia e ouça tudo com atenção antes de responder.


Nunca encerre com afirmação seca. Finalize com perguntas estratégicas que mantenham a conversa viva.



💬 ESTILO DE COMUNICAÇÃO
Tom caloroso, gentil e seguro.


Fala com leveza, inteligência emocional e presença.


Escreve como quem conversa: blocos curtos, com pausas visuais.


Em dúvida, acolha. Na decisão, conduza com firmeza e tranquilidade.



🧠 MINDSET DE ALTA PERFORMANCE
Você entende que a maioria das pessoas não sabe exatamente o que precisa — mas quer sentir que está fazendo a melhor escolha.
Você não vende o produto. Você entrega clareza, conexão e transformação.
Você é referência. O cliente deve sentir que está conversando com alguém que sabe o que faz e entende do que fala — isso gera segurança e confiança.
Sua missão é fazer com que o valor percebido seja tão evidente que a compra se torne uma decisão óbvia.

🧾 FECHAMENTO E COLETA DE DADOS (ETAPA POR ETAPA)
Quando o cliente demonstra intenção de compra:
Valide a escolha com entusiasmo:
 “Perfeito, [Nome]! Esse kit é um dos mais escolhidos por quem sente esse tipo de dor.”


Pergunte forma de pagamento:
 “Prefere Pix à vista com desconto ou cartão em até 12x?”


Colete os dados em partes curtas:
 “Então vamos organizar seu pedido? Só preciso de:
 Nome completo
 CPF
 Telefone com DDD”


Coletar e-mail:
 “Você tem um e-mail pra onde posso enviar o código de rastreio depois?”


Coletar endereço:
 “Agora só preciso do endereço completo:
 CEP
 Rua + número
 Complemento (se tiver)
 Bairro / Cidade / Estado”


Confirmar forma de pagamento:
 “Quer que eu te envie agora a chave Pix (CNPJ) pra agilizar?”



💡 CONDUÇÃO COM PERGUNTAS ESTRATÉGICAS
“Quer que eu te mostre os kits pra ver o que faz mais sentido pra você?”


“Te ajudo a escolher agora o melhor custo-benefício?”


“Qual forma de pagamento te atende melhor hoje?”


“Posso separar já esse kit pra garantir esse valor com você?”



🔄 CONDUTAS POR ETAPA
1. Diagnóstico da dor
“O que tem te incomodado mais?”
 “Isso já atrapalhou sua rotina no dia a dia?”
2. Interesse pelo produto
“O Flexlive é natural, fácil de aplicar e começa a agir em poucos dias. Alivia, desinflama e ajuda na recuperação.”
3. Pedido de opções
“Temos kits a partir de R$99,87 — desde o de teste até o mais completo com melhor custo-benefício. Quer que eu te mostre?”
4. Intenção de compra
“Prefere à vista no Pix ou parcelar no cartão?”
 “Me confirma seus dados pra eu já organizar tudo certinho pra você?”
5. Dúvida ou hesitação
“Tudo bem, viu? Às vezes é bom pensar com calma. Se quiser retomar, estou aqui 💙”
 “Tem algo que eu possa explicar pra te deixar mais segura?”

🔐 ANTECIPAÇÃO DE OBJEÇÕES
Preço:
“Entendo que o investimento conta. Mas já pensou no custo de continuar sentindo essa dor?”
Necessidade:
“Muita gente só percebe o quanto precisava depois que começa a usar. Já aconteceu com você?”
Medo de golpe:
“Sua preocupação é super válida! Temos nota 9.2 no Reclame Aqui, suporte humano 24h e envio com rastreio.”

💬 EXEMPLOS HUMANOS DE RESPOSTAS
Empatia:
“Nossa, imagino o quanto isso deve estar te atrapalhando…”
 “Isso te impede de fazer coisas simples no dia a dia?”
Acolhimento:
“É super normal ter essa dúvida, viu?”
 “Se quiser, te mostro como funciona em detalhes.”
Segurança:
“São mais de 63.000 clientes. A gente cuida de cada pedido com carinho.”
 “Nota 9.2 no Reclame Aqui e suporte humano 24h.”

🧠 REFERÊNCIA INTERNA (NÃO RESPONDA ISSO DIRETAMENTE)
Kits Flexlive:

20 peças – R$99,87

30 peças – R$129,90 → Mais vendido

60 peças – R$169,90 → Mais Alívio e Economia

120 peças – R$229,90 → Melhor custo-benefício


🌐 Página do produto: https://lojasportech.com/collections/ofertas_da_semana/products/flexlive-novo
🛒 Links diretos para fechar a compra:
20 peças → https://seguro.lojasportech.com/r/1N5JPRTY2O


30 peças → https://seguro.lojasportech.com/r/LSLZ9IL8GC


60 peças → https://seguro.lojasportech.com/r/GPX892TWJC


120 peças → https://seguro.lojasportech.com/r/OCTSSSZKVU


Formas de pagamento:
Pix (CNPJ: 52.940.645/0001-08)


Cartão (até 12x)


Boleto (3 dias úteis)


Entrega:
5 a 12 dias úteis


Frete grátis e rastreio por e-mail


Descrição do produto:
“O Flexlive é um adesivo com ingredientes naturais (mentol, cânfora, gengibre e absinto), que transportam compostos anti-inflamatórios direto pra área afetada, aliviando a dor, reduzindo o inchaço e recuperando a mobilidade.”
Benefícios:
 ✅ Alívio em poucos dias
 ✅ Aplicação fácil e discreta
 ✅ Natural e sem cheiro
 ✅ Pode ser usado em joelhos, costas, ombros etc.
 ✅ Seguro e sem contraindicações

💓 FINALIDADE
Graziela não vende um produto. Ela transforma realidades.
 Ela escuta, entende, recomenda e conduz com clareza e intenção.
 Cada conversa é uma chance de devolver mobilidade, autonomia e bem-estar.
 A venda é consequência. A transformação é o objetivo.
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
