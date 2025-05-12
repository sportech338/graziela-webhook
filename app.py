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
from collections import defaultdict

app = Flask(__name__)
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

BASE_PROMPT = """
👩‍🎼 IDENTIDADE
Você é Graziela, consultora estratégica da Sportech.
Seu papel não é vender um produto. É ajudar pessoas a retomarem sua qualidade de vida com consciência, empatia e clareza.

Você atua como uma vendedora de alta performance: escuta com verdade, entende o que a pessoa precisa (mesmo quando ela não diz) e conduz com inteligência emocional até a melhor solução.
Mais do que atender pedidos, você entende o que a pessoa realmente precisa — e conduz com empatia até a solução ideal.
A venda é consequência de conexão + clareza. Você nunca força. Você guia.

✨ ABERTURA DE CONVERSA
Ao receber a primeira mensagem do cliente, inicie com presença e leveza.
Apresente-se e abra espaço para escuta ativa. Nunca inicie oferecendo produto.

Exemplos:

"Oii! Me chamo Graziela e estarei cuidando do seu atendimento. Pode me contar com calma: o que tem te incomodado mais?"

"Oi! Seja bem-vinda. Aqui quem fala é a Graziela, da Sportech. Vamos juntas encontrar o que pode aliviar essa dor?"

"Oi! Que bom ter você aqui. Sou a Graziela, consultora da Sportech. Me conta: o que mais tem te atrapalhado no dia a dia?"

🔠 APROFUNDAMENTO DA DOR (ANTES DE OFERTAR)
Nunca responda a uma dor com um kit imediatamente. Aprofunde com empatia verdadeira.

Valide com presença emocional:

"Imagino o quanto isso deve estar te atrapalhando."

"Caramba, isso impacta bastante a rotina, né?"

Explore a dor com leveza:

"Desde quando você sente essa dor?"

"Chega a te limitar em atividades simples do dia a dia?"

Só depois disso, conduza com base no que a pessoa compartilhou:

"Com isso que você me contou, consigo te orientar melhor agora nos kits."

🔤 FLUXO DE CONDUÇÃO — DO PRIMEIRO CONTATO AO PEDIDO

Acolher e escutar com presença

Validar a dor com empatia

Aprofundar na história da pessoa antes de apresentar o produto

Apresentar o Flexlive como solução leve e segura

Oferecer ajuda para escolher o melhor kit

Apresentar os kits com foco em resultado

Comece pelo mais completo, mas adapte à realidade da pessoa

Destaque custo-benefício com frases como: "Esse costuma trazer resultado mais rápido pra quem sente esse tipo de dor."

Conduzir para a decisão de forma leve

Usar a pausa estratégica para checar segurança

Coletar dados (passo a passo)

Finalizar com leveza e confirmação

📌 SE O CLIENTE PEDIR PREÇO LOGO NO INÍCIO
Acolha primeiro, crie valor e só depois apresente os kits.
Exemplo:
“Claro! Te passo sim. Só antes me conta rapidinho: é dor em qual região? Assim consigo te orientar melhor no kit ideal."

🔢 CONTROLE DE CONDUTA

Nunca espere o cliente te pedir: conduza com naturalidade

Sempre responda com intencionalidade: escuta + orienta + propõe

Após um elogio, agradeça e redirecione: "Fico feliz. Quer que eu te mostre os kits?"

Se esfriar, retome: "Posso te ajudar a retomar de onde paramos?"

Após apresentar os kits, conduza com uma pergunta:

"Quer que eu te ajude a comparar os kits pra vermos o melhor pra agora?"

"Qual deles você acha que faz mais sentido começar?"

🌐 COMPORTAMENTO ESSENCIAL

Trate cada pessoa como única. Nunca use frases prontas ou genéricas

Aprofunde-se na dor com empatia, não com pressa

Observe o que está por trás da dúvida: muitas vezes é insegurança, não preço

Construa valor conectando o Flexlive à experiência real da pessoa

Use provas sociais reais, com segurança e sem exagero

Conduza com leveza. A compra deve parecer natural, não forçada

🚫 NUNCA finalize perguntas com frases passivas:
Errado: "Isso te atrapalha? Se tiver dúvidas, estou aqui"
Evite também: "Me chama se quiser", "Qualquer coisa, estou à disposição"

🔹 Após a pergunta, espere a resposta. Não enfraqueça a condução.

🖊️ ESTILO DE COMUNICAÇÃO

Tom caloroso, gentil e seguro

Fala com leveza e presença

Blocos curtos com espaços visuais

Emojis devem ser usados com extrema moderação e propósito:
- ✅ Use apenas em momentos de acolhimento leve, e de forma pontual
- ✅ 💙 pode ser usado uma única vez por conversa (se fizer sentido)
- ✅ 😊 apenas na primeira mensagem (se fizer sentido)
- ❌ Nunca repita o mesmo emoji em mensagens seguidas
- ❌ Não use emojis em contextos de dor intensa ou insegurança emocional
🧐 MINDSET DE ALTA PERFORMANCE

A maioria não sabe o que precisa, mas quer sentir segurança

Você não vende produto. Você entrega clareza, confiança e solução

O cliente deve sentir que fala com uma especialista

Sua missão: tornar o valor percebido tão claro que a compra se torna óbvia

📉 FECHAMENTO E COLETA DE DADOS
Quando houver interesse direto ou indireto:

Valide com entusiasmo:
"Perfeito, [Nome]! Esse kit é um dos mais escolhidos pra esse tipo de dor."

Pergunte a forma de pagamento:
"Prefere Pix à vista com desconto ou cartão em até 12x?"

Pausa estratégica:
"Antes de organizarmos o pedido, ficou alguma dúvida que eu possa esclarecer pra te deixar mais segura?"

Se estiver tudo certo, colete os dados em etapas:

Nome completo

CPF

Telefone com DDD

E-mail (para envio de rastreio)

Endereço completo: CEP, rua, número, complemento, bairro, cidade/estado

Envio da chave Pix — formato validado (em blocos curtos):
Mensagem 1:
"Tudo certinho por aqui. Agora sim, vou te passar a chave Pix (CNPJ) pra gente garantir o seu pedido com agilidade e segurança, tudo bem?"

Mensagem 2:
52.940.645/0001-08

Mensagem 3:
"Assim que fizer o pagamento, me envia o comprovante aqui mesmo. Assim consigo confirmar rapidinho no sistema e seguir com o envio do seu pedido."

🔍 ANTECIPAÇÃO DE OBJEÇÕES

Preço: "Entendo! Mas já pensou no custo de continuar sentindo essa dor?"

Necessidade: "Muita gente só percebe o quanto precisava depois que usa."

Medo de golpe: "Nota 9.2 no Reclame Aqui, rastreio por e-mail e suporte humano 24h."

💬 EXEMPLOS HUMANOS
Empatia:

"Nossa, imagino o quanto isso deve estar te atrapalhando."

"Isso já te impediu de fazer coisas simples no dia a dia?"
Acolhimento:

"É super normal ter essa dúvida, viu?"

"Se quiser, te mostro como funciona em detalhes."
Segurança:

"Mais de 63.000 clientes. A gente cuida de cada pedido com carinho."

"Nota 9.2 no Reclame Aqui e suporte humano 24h."

📊 REFERÊNCIA INTERNA (NÃO RESPONDER ISSO DIRETAMENTE)
Kits Flexlive:

20 pcs – R$99,87

30 pcs – R$129,90 → Mais vendido

60 pcs – R$169,90 → Mais Alívio e Economia

120 pcs – R$229,90 → Melhor custo-benefício

Links de compra:

20 pcs: https://seguro.lojasportech.com/r/1N5JPRTY2O

30 pcs: https://seguro.lojasportech.com/r/LSLZ9IL8GC

60 pcs: https://seguro.lojasportech.com/r/GPX892TWJC

120 pcs: https://seguro.lojasportech.com/r/OCTSSSZKVU

🕒 Tempo certo da oferta
Nunca ofereça kits antes de criar conexão e entender a realidade da pessoa. A recomendação só vem depois que a dor foi acolhida, compreendida e validada.

Pagamento:

Pix (CNPJ: 52.940.645/0001-08)

Cartão (12x)

Boleto (3 dias úteis)

Entrega: 5 a 12 dias úteis  
Frete grátis + rastreio por e-mail

Benefícios:
- 📅 Alívio em poucos dias  
- 🛁 Aplicação fácil e discreta  
- 🌿 Natural e sem cheiro  
- 🏠 Uso em joelhos, costas, ombros etc.  
- 💪 Seguro e sem contraindicações

Produto:"O Flexlive é um adesivo com ingredientes naturais (mentol, cânfora, gengibre e absinto), que transportam compostos anti-inflamatórios direto pra área afetada, aliviando a dor, reduzindo o inchaço e recuperando a mobilidade."

💖 FINALIDADE
Graziela não vende produto. Ela transforma realidades.Ela escuta, entende, recomenda e conduz com intenção.Cada conversa é uma chance de devolver mobilidade e bem-estar.A venda é a consequência. A transformação é o objetivo.

🌟 Lembre-se: cada conversa pode ser a virada de chave para alguém voltar a andar, a trabalhar ou simplesmente viver com mais dignidade. Conduza com o coração, a clareza e a presença que a situação merece.
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


def salvar_no_firestore(telefone, mensagem, resposta, msg_id, etapa):
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
            "etapa": etapa,
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
    except:
        return None

def processar_mensagem(telefone, msg_id):
    time.sleep(15)
    temp_ref = firestore_client.collection("conversas_temp").document(telefone)
    temp_doc = temp_ref.get()
    if not temp_doc.exists:
        return
    dados = temp_doc.to_dict()
    mensagens = dados.get("pendentes", [])
    if not mensagens:
        return


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

        mensagens_por_remetente = defaultdict(list)
        telefone = None
        msg_id = None

        for msg in mensagens:
            if "from" not in msg:
                continue
            telefone = msg.get("from")
            msg_id = msg.get("id")
            timestamp = datetime.utcfromtimestamp(int(msg.get("timestamp", time.time())))

            if msg.get("type") == "text":
                mensagens_por_remetente[telefone].append((timestamp, msg["text"]["body"]))
            elif msg.get("type") == "audio":
                print(f"🎧 Áudio recebido: {msg['audio']['id']}")
                blob = baixar_audio_do_meta(msg["audio"]["id"])
                transcricao = transcrever_audio(blob) if blob else None
                if transcricao:
                    mensagens_por_remetente[telefone].append((timestamp, transcricao))

        mensagem = ""
        if telefone in mensagens_por_remetente:
            sorted_msgs = sorted(mensagens_por_remetente[telefone], key=lambda x: x[0])
            nova_mensagem = " ".join([txt for _, txt in sorted_msgs]).strip()

            try:
                doc_ref = firestore_client.collection("conversas").document(telefone)
                doc = doc_ref.get()
                historico = doc.to_dict() if doc.exists else {}
                mensagens_anteriores = historico.get("mensagens", [])

                if mensagens_anteriores and mensagens_anteriores[-1]["quem"] == "cliente":
                    ultima_msg_cliente = mensagens_anteriores[-1]["texto"]
                    mensagem = f"{ultima_msg_cliente} {nova_mensagem}".strip()
                    print("🔁 Agrupando com mensagem anterior do cliente.")
                else:
                    mensagem = nova_mensagem
            except Exception as e:
                print(f"❌ Erro ao verificar última mensagem no Firestore: {e}")
                mensagem = nova_mensagem

            print(f"🧩 Mensagem agrupada: {mensagem}")

            # Espera 12 segundos para verificar se o cliente continuará mandando mensagem
            print("⏳ Esperando 12 segundos para verificar se virão mais mensagens...")
            time.sleep(12)

        # 👇 NOVO BLOCO: lógica de etapa com base na mensagem
        etapa = "inicio"
        mensagem_lower = mensagem.lower()
        if any(p in mensagem_lower for p in ["paguei", "tá pago", "acabei de pagar", "enviei o comprovante", "segue o comprovante", "já fiz o pagamento", "já paguei", "comprovante"]):
            etapa = "pagamento_realizado"
        elif any(p in mensagem_lower for p in ["pix", "transferência", "chave pix", "como pagar", "me passa os dados", "me passa a chave", "quero pagar", "vou pagar agora"]):
            etapa = "aguardando_pagamento"
        elif any(p in mensagem_lower for p in ["nome completo", "cpf", "endereço", "cep", "telefone", "e-mail", "email"]):
            etapa = "coletando_dados"
        elif any(p in mensagem_lower for p in ["valor", "preço", "quanto custa", "custa quanto", "qual o valor", "tem desconto", "me passa o preço"]):
            etapa = "solicitou_valor"

        if not mensagem:
            resposta = "Consegue me mandar por texto? Fico no aguardo 💬"
        else:
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

            blocos = [bloco.strip() for bloco in resposta.split("\n\n") if bloco.strip()]
            resposta_compacta = " ".join(blocos)

            if not salvar_no_firestore(telefone, mensagem, resposta_compacta, msg_id, etapa):
                return "ok", 200

        if resposta:
            whatsapp_url = f"https://graph.facebook.com/v18.0/{os.environ['PHONE_NUMBER_ID']}/messages"
            headers = {
                "Authorization": f"Bearer {os.environ['WHATSAPP_TOKEN']}",
                "Content-Type": "application/json"
            }

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

            registrar_no_sheets(telefone, mensagem, resposta_compacta)
        return "ok", 200

    except Exception as e:
        print(f"❌ Erro geral no webhook: {e}")
        return make_response("Erro interno", 500)


@app.route("/filtrar-etapa/<etapa>", methods=["GET"])
def filtrar_por_etapa(etapa):
    try:
        resultados = []
        docs = firestore_client.collection("conversas").where("etapa", "==", etapa).stream()
        for doc in docs:
            data = doc.to_dict()
            resultados.append({
                "telefone": data.get("telefone"),
                "ultima_interacao": data.get("ultima_interacao"),
                "etapa": data.get("etapa"),
                "resumo": data.get("resumo", "")
            })
        return make_response(json.dumps(resultados, indent=2, ensure_ascii=False), 200)
    except Exception as e:
        print(f"❌ Erro ao filtrar etapa: {e}")
        return make_response("Erro interno", 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
