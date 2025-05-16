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
from google.oauth2 import service_account
import time
from collections import defaultdict
import threading
import re
from rapidfuzz import fuzz
from textwrap import shorten

app = Flask(__name__)
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

BASE_PROMPT = """⚠️ Regra essencial: nunca envie duas perguntas diretas na mesma resposta. Isso prejudica o tom consultivo e sobrecarrega o cliente.

👩‍🎼 IDENTIDADE

Você é Graziela, consultora estratégica da Sportech.  
Seu papel não é vender produtos, e sim ajudar pessoas a retomarem sua qualidade de vida com consciência, empatia e clareza.

Você atua como uma vendedora de alta performance:  
- Escuta com verdade  
- Entende o que a pessoa precisa (mesmo sem ela dizer)  
- Conduz com inteligência emocional até a melhor solução  
- A venda é consequência de conexão + clareza  
- Nunca força. Sempre guia

🟢 ABERTURA DA CONVERSA

- Sempre que iniciar uma nova conversa, apresente-se de forma leve e acolhedora e use esse emoji "😊" no final.  
- Nunca fale do produto na abertura. Foque em criar conexão.  
- Após a apresentação, convide a pessoa a contar mais sobre o que sente, com 1 única pergunta direta por vez.
- Nunca inicie com explicações técnicas  

✨ TOM E ESTILO DE CONVERSA

- Use \\n\\n para separar blocos e criar pausas naturais  
- Respostas curtas = 1 bloco  
- Respostas com acolhimento/orientação = 2 ou mais blocos  
- Nunca escreva duas ou mais perguntas diretas em uma mesma mensagem.
- Se quiser fazer mais de uma pergunta, escolha apenas uma e deixe a outra para a próxima resposta.
- Evite terminar blocos com duas interrogações seguidas. Isso quebra o ritmo da conversa e deixa o cliente confuso.
- Nunca use emojis em contextos de dor intensa  
- Nunca finalize com frases passivas como “estou à disposição”  

📏 FLUXO NATURAL DA CONVERSA

1. Acolher e escutar com presença  
2. Validar a dor com empatia  
3. Aprofundar na história da pessoa  
4. Apresentar o Flexlive como solução  
5. Ajudar a escolher o melhor kit  

✅ Exemplo sugerido de condução:  
"Desde quando você sente essa dor?"  
(aguarde resposta antes de perguntar mais)

🔠 DOR ANTES DA OFERTA

- Nunca responda sobre a dor do cliente com produto logo de cara  
- Sempre valide com empatia verdadeira  
- Faça pausa consultiva antes de transicionar  

🧐 MINDSET DE ALTA PERFORMANCE

- As pessoas querem se sentir seguras  
- Graziela entrega clareza e solução, não só produto  
- A venda vem quando o valor é claro  
- O cliente deve sentir que fala com uma especialista  

💡 APRESENTAÇÃO DOS KITS

- Apresente todos os kits (comece pelo de 30 peças – mais vendido)  
- Destaque os benefícios de forma consultiva  
- Adapte à realidade do cliente  
- Sugira com fala humana e sincera:
"Se for pra te dar uma dica sincera: o de 30 costuma ser o mais escolhido por quem tá começando..."  
- Se preferir o de 20, acolha:
  "Claro! O importante é a gente começar de algum jeito, né?"

📌 SE PEDIR PREÇO LOGO

- Se a pessoa pedir o preço logo no início da conversa:
- Nunca ignore a pergunta sobre o valor.
- Acolha com empatia e valide que o preço é importante.
- Informe que vai passar o valor, mas só depois de entender melhor a situação da pessoa.
- Explique que isso é necessário para indicar a melhor solução com clareza e personalização.
- Finalize com uma pergunta única e sincera que ajude a contextualizar (ex: como ela está se sentindo, o que motivou o contato, etc).
🛑 Nunca envie duas perguntas diretas. Sempre uma só.
✅ A resposta deve soar natural, consultiva e acolhedora, não robótica.
👉 Gere a resposta de forma empática e fluida, respeitando esses critérios. 

🔢 FECHAMENTO

Confirmar se ficou alguma dúvida -> Cadastro -> Endereço -> Forma de pagamento -> Venda (Chave pix ou link cartão)

Valide o interesse:  
“Perfeito, [Nome]! Esse kit é um dos mais escolhidos pra esse tipo de dor.”  
“Antes de organizarmos o pedido, ficou alguma dúvida que eu possa esclarecer?”

1. Coleta de Dados Pessoais  
"Perfeito! Vamos garantir seu pedido com segurança."  
"Para começar, vou precisar de alguns dados seus:  
- Nome completo:  
- CPF:  
- Telefone com DDD:

Apresenta algum e-mail para envio do código de rastreio?"

2. Coleta de Endereço  
"Agora, vamos precisar do seu endereço completo:  
- CEP:  
- Endereço completo:  
- Número:  
- Complemento (opcional):"  
"Assim que tiver tudo certinho, seguimos com a finalização do pedido."

3. Pagamento  
"Prefere Pix à vista com desconto ou cartão em até 12x?"  

Pix (em blocos):  
"Excelente! Abaixo, vou te passar a chave Pix (CNPJ) pra gente garantir o seu pedido com agilidade e segurança, tudo bem?"  
52.940.645/0001-08  
"Assim que fizer o pagamento, me envia o comprovante aqui mesmo. Assim consigo confirmar rapidinho no sistema e seguir com o envio do seu pedido."

🔍 OBJEÇÕES

- Preço: "Já pensou no custo de continuar com essa dor?"  
- Necessidade: "Muita gente só percebe o quanto precisava depois que usa."  
- Medo de golpe: "Nota 9.2 no Reclame Aqui, rastreio por e-mail e suporte humano 24h."

💬 FRASES HUMANAS

Empatia:  
"Nossa, imagino o quanto isso deve estar te atrapalhando."  
"Isso já te impediu de fazer coisas simples no dia a dia?"

Acolhimento:  
"É super normal ter essa dúvida, viu?"  
"Se quiser, te mostro como funciona em detalhes."

Segurança:  
"Mais de 63.000 clientes. A gente cuida de cada pedido com carinho."  
"Nota 9.2 no Reclame Aqui e suporte humano 24h."

📦 REFERÊNCIA INTERNA (NÃO RESPONDER DIRETAMENTE)

Kits e preços:  
- 20 peças – R$99,87  
- 30 peças – R$129,90 → Mais vendido  
- 60 peças – R$169,90 → Mais alívio e economia  
- 120 peças – R$229,90 → Melhor custo-benefício  

Links:  
20 peças: https://seguro.lojasportech.com/r/1N5JPRTY2O  
30 peças: https://seguro.lojasportech.com/r/LSLZ9IL8GC  
60 peças: https://seguro.lojasportech.com/r/GPX892TWJC  
120 peças: https://seguro.lojasportech.com/r/OCTSSSZKVU  

Pagamento:  
Pix (CNPJ): 52.940.645/0001-08  
Cartão (até 12x) - Sendo 2x sem juros
Boleto (3 dias úteis)

Entrega:  
- 5 a 12 dias úteis  
- Frete grátis + rastreio por e-mail  

Benefícios:  
- Alívio em poucos dias  
- Aplicação fácil e discreta  
- Natural e sem cheiro  
- Uso em joelhos, costas, ombros  
- Seguro e sem contraindicações  

Produto:  
“O Flexlive é um adesivo com ingredientes naturais (mentol, cânfora, gengibre e absinto), que transportam compostos anti-inflamatórios direto pra área afetada, aliviando a dor, reduzindo o inchaço e recuperando a mobilidade.”

💖 PROPÓSITO

Graziela não vende produto. Ela transforma realidades.  
Cada conversa pode ser a virada de chave pra alguém voltar a viver com dignidade.  
Conduza com coração, clareza e presença.

⚠️ Regra essencial: nunca envie duas perguntas diretas na mesma resposta. Isso prejudica o tom consultivo e sobrecarrega o cliente."""

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SPREADSHEET_NAME = "Histórico de conversas | Graziela"


encoded = os.environ.get("GOOGLE_CREDENTIALS_BASE64")
if not encoded:
    raise ValueError("Variável GOOGLE_CREDENTIALS_BASE64 não encontrada.")

decoded = base64.b64decode(encoded).decode("utf-8")
info = json.loads(decoded)

# Usa o dict para criar as credenciais
credentials = service_account.Credentials.from_service_account_info(info)
firestore_client = firestore.Client(credentials=credentials, project=info["project_id"])


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

ETIQUETA_PRIORIDADE = {
    "Venda feita": 5,
    "Venda perdida": 4,
    "Agendado": 3,
    "Em negociação": 2,
    "Interessado": 1
}

def analisar_estado_comportamental(mensagem):
    mensagem = mensagem.lower().strip()

    def fuzzy(padroes):
        return fuzzy_match(mensagem, padroes, limiar=85)

    # 🔍 Consciência
    if fuzzy(["dói muito", "dor no", "minha dor", "tá doendo", "não consigo andar", "tô cansado dessa dor"]):
        consciencia = "Sabe da dor"
    elif fuzzy(["já tentei de tudo", "nada resolve", "já usei isso", "não resolveu"]):
        consciencia = "Sabe da solução"
    elif fuzzy(["quero o flexlive", "quero o de 30", "prefiro pix", "tem o de 60 peças"]):
        consciencia = "Sabe do produto"
    elif fuzzy(["já fiz o pix", "vou querer o de 120", "pode fechar", "meu cpf é"]):
        consciencia = "Já quer comprar"
    else:
        consciencia = "Pouco consciente"

    # 🙅 Objeção
    if fuzzy(["tá caro", "sem dinheiro", "desconto", "valor alto"]):
        objecao = "Preço"
    elif fuzzy(["parece golpe", "tem garantia", "é seguro", "não confio"]):
        objecao = "Confiança"
    elif fuzzy(["vou pensar", "ainda não sei", "mais pra frente", "estou em dúvida"]):
        objecao = "Indecisão"
    elif fuzzy(["não me interessa", "não uso essas coisas", "já resolvi meu problema"]):
        objecao = "Necessidade"
    else:
        objecao = "Nenhuma"

    return {
        "consciencia": consciencia,
        "objeção": objecao
    }


def detectar_etiqueta(mensagem, tentativas=1):
    mensagem = mensagem.lower().strip()

    def fuzzy(padroes):
        return fuzzy_match(mensagem, padroes, limiar=85)

    if tentativas >= 18 or fuzzy(["não quero mais", "cancela", "desiste", "quero cancelar"]):
        return "Venda perdida"
    elif fuzzy(["comprovante", "paguei", "tá pago", "já fiz o pix", "enviei o pagamento"]):
        return "Venda feita"
    elif fuzzy(["me chama", "às", "dia", "horário", "horas", "amanhã", "depois das", "semana que vem"]):
        return "Agendado"
    elif fuzzy(["valor", "preço", "quanto custa"]):
        return "Em negociação"
    else:
        return "Interessado"


def atualizar_etiqueta(etiqueta_atual, nova_etiqueta):
    prioridade_atual = ETIQUETA_PRIORIDADE.get(etiqueta_atual, 0)
    prioridade_nova = ETIQUETA_PRIORIDADE.get(nova_etiqueta, 0)

    if nova_etiqueta == "Venda perdida" and etiqueta_atual != "Venda feita":
        print(f"⚠️ Rebaixando etiqueta para 'Venda perdida' por cancelamento ou abandono.")
        return "Venda perdida"

    if prioridade_nova > prioridade_atual:
        print(f"🔁 Etiqueta atualizada: {etiqueta_atual} → {nova_etiqueta}")
        return nova_etiqueta

    print(f"🔒 Etiqueta mantida: {etiqueta_atual} (nova tentativa: {nova_etiqueta})")
    return etiqueta_atual

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
        tentativas = data.get("tentativas", 0) + 1
        agora = datetime.now()

        mensagens.append({"quem": "cliente", "texto": mensagem, "timestamp": agora.isoformat()})
        mensagens.append({"quem": "graziela", "texto": resposta, "timestamp": agora.isoformat()})

        if len(mensagens) > 40:
            texto_completo = "\n".join([f"{'Cliente' if m['quem']=='cliente' else 'Graziela'}: {m['texto']}" for m in mensagens])
            novo_resumo = resumir_historico(texto_completo)
            resumo_completo = f"{resumo.strip()}\n{novo_resumo.strip()}".strip()
            resumo = shorten(resumo_completo, width=2000, placeholder="...")
            mensagens = mensagens[-6:]
            print("📉 Mensagens antigas resumidas.")

        estado = analisar_estado_comportamental(mensagem)
        etiqueta_nova = detectar_etiqueta(mensagem, tentativas)
        etiqueta_final = atualizar_etiqueta(data.get("etiqueta", "Interessado"), etiqueta_nova)

        atualizacao = {
            "telefone": telefone,
            "etapa": etapa,
            "ultima_interacao": agora,
            "mensagens": mensagens,
            "resumo": resumo,
            "last_msg_id": msg_id,
            "tentativas": tentativas,
            "nivel_consciencia": estado["consciencia"],
            "objecao_atual": estado["objeção"],
            "etiqueta": etiqueta_final
        }

        if 'novo_resumo' in locals() and novo_resumo:
            atualizacao["ultimo_resumo_em"] = agora.isoformat()

        doc_ref.set(atualizacao, merge=True)
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
            contexto = f"{resumo}\n" + "\n".join(linhas) if resumo else "\n".join(linhas)

            # Pega emojis já usados nas últimas mensagens da Graziela
            texto_respostas = " ".join([m["texto"] for m in mensagens if m["quem"] == "graziela"])
            emojis_ja_usados = [e for e in ["😊", "💙", "😔"] if e in texto_respostas]

            return contexto, emojis_ja_usados
    except Exception as e:
        print(f"❌ Erro ao obter contexto: {e}")
    return "", []


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
        if res.status_code != 200 or "text" not in res.json():
            raise Exception("Falha na transcrição.")
        return res.json()["text"]
    except Exception as e:
        print(f"❌ Erro na transcrição de áudio: {e}")
        return None

def quebrar_em_blocos_humanizado(texto, limite=350):
    blocos = []
    tempos = []

    # Respeita blocos separados por \n\n (sugestão vinda do próprio GPT)
    for trecho in texto.split("\n\n"):
        trecho = trecho.strip()
        if not trecho:
            continue

        # Se o bloco já está dentro do limite, adiciona direto
        if len(trecho) <= limite:
            blocos.append(trecho)
        else:
            # Caso ultrapasse, faz uma quebra mais inteligente em frases
            partes = re.split(r'(?<=[.!?]) +', trecho)
            paragrafo = ""
            for parte in partes:
                if len(paragrafo) + len(parte) + 1 <= limite:
                    paragrafo += (" " if paragrafo else "") + parte
                else:
                    blocos.append(paragrafo.strip())
                    paragrafo = parte
            if paragrafo:
                blocos.append(paragrafo.strip())

    # Definindo os tempos de espera entre blocos
    for i, bloco in enumerate(blocos):
        if i == 0:
            tempos.append(15)
        elif len(bloco) > 250:
            tempos.append(6)
        elif len(bloco) > 100:
            tempos.append(4)
        else:
            tempos.append(2)

    return blocos, tempos

def remover_emojis_repetidos(texto, emojis_ja_usados):
    emojis_validos = ["😊", "💙", "😔"]
    novos_emojis_usados = []

    for emoji in emojis_validos:
        ocorrencias = [m.start() for m in re.finditer(re.escape(emoji), texto)]
        if emoji in emojis_ja_usados and ocorrencias:
            texto = texto.replace(emoji, "", len(ocorrencias))  # remove todas
        elif ocorrencias:
            texto = texto.replace(emoji, "", len(ocorrencias) - 1)
            novos_emojis_usados.append(emoji)

    return texto, novos_emojis_usados

def fuzzy_match(texto, padroes, limiar=85):
    return any(fuzz.partial_ratio(texto, padrao) >= limiar for padrao in padroes)

def identificar_proxima_etapa(resposta_lower):
    etapas = {
        "momento_conexao": [
            "imagino o quanto", "isso impacta", "entendo demais", "pesado conviver",
            "vamos juntas", "me conta", "vamos juntas encontrar", "diz muito sobre você", "abrir mão disso", "deve ser difícil conviver"
        ],
        "apresentando_preço": [
            "com base no que você compartilhou", "posso te mostrar os kits",
            "vou te apresentar as opções", "valores são", "kit mais vendido", "custam", "valor", "preço", "quanto custa", "tem desconto"
        ],
        "coletando_dados_pessoais": [
            "vou precisar dos seus dados", "preciso de algumas informações suas",
            "pra garantir seu pedido", "vamos garantir seu pedido", "dados pessoais", "nome completo", "cpf", "telefone com ddd"
        ],
        "coletando_endereco": [
            "vamos precisar do seu endereço", "endereço completo", "cep", "número", "bairro", "complemento (opcional)"
        ],
        "metodo_pagamento": [
            "prefere pix", "cartão em até 12x", "forma de pagamento", "como prefere pagar"
        ],
        "aguardando_pagamento": [
            "vou te passar a chave pix", "chave pix (cnpj)", "abaixo segue a chave", "para garantir seu pedido via pix"
        ],
        "pagamento_confirmado": [
            "me envia o comprovante", "confirmar rapidinho no sistema", "envia aqui o pagamento", "assim consigo confirmar"
        ]
    }

    for etapa, frases in etapas.items():
        if fuzzy_match(resposta_lower, frases, limiar=85):
            return etapa

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
                temp_ref = firestore_client.collection("conversas_temp").document(telefone)
                temp_doc = temp_ref.get()
                pendentes = temp_doc.to_dict().get("pendentes", []) if temp_doc.exists else []

                pendentes.append({
                    "texto": nova_mensagem,
                    "timestamp": datetime.utcnow().isoformat(),
                    "msg_id": msg_id
                })

                temp_ref.set({"pendentes": pendentes})
                print("⏳ Mensagem adicionada à fila temporária.")

                status_doc = firestore_client.collection("status_threads").document(telefone)
                if not status_doc.get().exists:
                    status_doc.set({"em_execucao": True})
                    threading.Thread(target=processar_mensagem, args=(telefone,)).start()

            except Exception as e:
                print(f"❌ Erro ao adicionar à fila temporária: {e}")

        return "ok", 200

    except Exception as e:
        print(f"❌ Erro geral no webhook: {e}")
        return make_response("Erro interno", 500)

def processar_mensagem(telefone):
    time.sleep(15)
    temp_ref = firestore_client.collection("conversas_temp").document(telefone)
    temp_doc = temp_ref.get()
    if not temp_doc.exists:
        return

    dados = temp_doc.to_dict()
    mensagens = dados.get("pendentes", [])
    if not mensagens:
        return

    mensagens_ordenadas = sorted(mensagens, key=lambda m: m["timestamp"])
    mensagem_completa = " ".join([m["texto"] for m in mensagens_ordenadas]).strip()
    msg_id = mensagens_ordenadas[-1]["msg_id"]

    print(f"🧩 Mensagem completa da fila: {mensagem_completa}")
    
    doc = firestore_client.collection("conversas").document(telefone).get()
    etapa = doc.to_dict().get("etapa", "inicio") if doc.exists else "inicio"

    prompt = [{"role": "system", "content": BASE_PROMPT}]
    contexto, emojis_ja_usados = obter_contexto(telefone)
    if contexto:
        prompt.append({"role": "user", "content": f"Histórico da conversa:\n{contexto}"})
    else:
        emojis_ja_usados = []
 
    prompt.append({
        "role": "user",
        "content": f"O cliente disse: \"{mensagem_completa}\"\n\nResponda como Graziela, seguindo o estilo e as regras do prompt."
    })

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=prompt,
        temperature=0.5,
        max_tokens=300
    )

    resposta = completion.choices[0].message.content.strip()
    print(f"🤖 GPT: {resposta}")
    resposta, novos_emojis = remover_emojis_repetidos(resposta, emojis_ja_usados)

    resposta_lower = resposta.lower()
    nova_etapa = identificar_proxima_etapa(resposta_lower)
    if nova_etapa and nova_etapa != etapa:
        print(f"🔁 Etapa atualizada automaticamente: {etapa} → {nova_etapa}")
        etapa = nova_etapa

    def contem_frase_proibida(texto):
        frases_proibidas = [
            "se tiver dúvidas, estou à disposição",
            "me chama se quiser",
            "qualquer coisa, estou por aqui"
        ]
        texto_lower = texto.lower()
        return any(frase in texto_lower for frase in frases_proibidas)

    if contem_frase_proibida(resposta):
        print("⚠️ Frase passiva proibida detectada. Requisitando reformulação automática...")
        reformulacao_prompt = [
            {"role": "system", "content": "Você é Graziela, consultora da Sportech. Reformule a mensagem anterior."},
            {"role": "user", "content": f"""Essa foi a resposta que você deu:

{resposta}

⚠️ Essa resposta termina com uma frase passiva que não conduz a conversa.

Reescreva de forma gentil e consultiva, **removendo a frase passiva** e encerrando com uma pergunta clara que incentive o cliente a continuar a conversa.

Mantenha os blocos curtos com até 350 caracteres e separados por **duas quebras de linha**."""}
        ]

        try:
            nova_resposta = client.chat.completions.create(
                model="gpt-4o",
                messages=reformulacao_prompt,
                temperature=0.4,
                max_tokens=300
            ).choices[0].message.content.strip()

            print("✅ Resposta reformulada automaticamente.")
            resposta = nova_resposta
            resposta, novos_emojis = remover_emojis_repetidos(resposta, emojis_ja_usados)

        except Exception as e:
            print(f"❌ Erro ao reformular resposta: {e}")
            resposta += "\n\n(Por favor, reformule com uma pergunta clara ao final)"

    resposta_normalizada = resposta.replace("\\n\\n", "\n\n").replace("\\n", "\n")
    blocos, tempos = quebrar_em_blocos_humanizado(resposta_normalizada, limite=350)
    print(f"🔹 Blocos finais para envio:\n{json.dumps(blocos, indent=2, ensure_ascii=False)}")
    resposta_compacta = "\n\n".join(blocos)

    etapas_delay = {
        "coletando_dados_pessoais": 15,
        "coletando_endereco": 15,
        "pagamento_realizado": 15,
        "aguardando_pagamento": 15
    }
    delay_inicial = etapas_delay.get(etapa, 15)
    if tempos:
        tempos[0] = delay_inicial

        doc_ref = firestore_client.collection("conversas").document(telefone)
        doc = doc_ref.get()
        if doc.exists and doc.to_dict().get("last_msg_id") == msg_id:
            print("⚠️ Mensagem já foi processada. Pulando salvar_no_firestore.")
        else:
            if not salvar_no_firestore(telefone, mensagem_completa, resposta_compacta, msg_id, etapa):
                return

    whatsapp_url = f"https://graph.facebook.com/v18.0/{os.environ['PHONE_NUMBER_ID']}/messages"
    headers = {
        "Authorization": f"Bearer {os.environ['WHATSAPP_TOKEN']}",
        
        "Content-Type": "application/json"
    }

    for i, (bloco, delay) in enumerate(zip(blocos, tempos)):
        payload = {
            "messaging_product": "whatsapp",
            "to": telefone,
            "text": {"body": bloco}
        }
        response = requests.post(whatsapp_url, headers=headers, json=payload)
        print(f"📤 Enviado bloco {i+1}/{len(blocos)}: {response.status_code} | {response.text}")
        time.sleep(delay)
        if response.status_code != 200:
            print(f"❌ Erro ao enviar bloco {i+1}: {response.text}")

    registrar_no_sheets(telefone, mensagem_completa, resposta_compacta)
    temp_ref.delete()
    firestore_client.collection("status_threads").document(telefone).delete()
    print("🧹 Fila temporária limpa.")
    print("🔁 Thread finalizada e status limpo.")

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
