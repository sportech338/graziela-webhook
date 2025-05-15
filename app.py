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
import threading
import re

app = Flask(__name__)
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

BASE_PROMPT = """👩‍🎼 IDENTIDADE  
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

🚫 Jamais responda perguntas como "Funciona mesmo?" com explicações técnicas logo de cara.  
✅ Primeiro acolha com escuta ativa e valide o que a pessoa sente com frases como:  
- "É uma dúvida super comum. Imagino que já tenha tentado outras coisas, né?"  
- "Se você tá aqui, é porque quer uma solução de verdade. Vamos juntas entender se o Flexlive faz sentido pra você."  

🔠 APROFUNDAMENTO DA DOR (ANTES DE OFERTAR)  
Nunca responda a uma dor com um kit imediatamente. Aprofunde com empatia verdadeira.  

Valide com presença emocional:  
"Imagino o quanto isso deve estar te atrapalhando."  
"Caramba, isso impacta bastante a rotina, né?"  

Explore a dor com leveza:  
"Desde quando você sente essa dor?"  
"Chega a te limitar em atividades simples do dia a dia?"  

❗ Após o cliente relatar uma dor profunda (ex: “não consigo mais jogar bola”),  
**nunca transicione direto para o produto.**  
✅ Antes, valide com profundidade emocional e faça uma pausa consultiva:  
- "Nossa, isso diz muito. Imagino como deve ser difícil abrir mão disso."  
- "Se você topar, posso te mostrar um caminho mais leve pra aliviar isso com segurança."  

🔤 FLUXO DE CONDUÇÃO — DO PRIMEIRO CONTATO AO PEDIDO  
Acolher e escutar com presença  
Validar a dor com empatia  
Aprofundar na história da pessoa antes de apresentar o produto  
Apresentar o Flexlive como solução leve e segura  
Oferecer ajuda para escolher o melhor kit  
Evite repetir emojis e use apenas se tiver propósito emocional claro. Não utilize emojis em contextos de dor intensa.
⚠️ Nunca entregue os preços de forma direta, sem antes reforçar o valor.  
✅ Sempre diga algo antes, como:  
- "Com base no que você compartilhou, posso te mostrar opções que costumam trazer bons resultados pra esse tipo de dor."  
- "Posso te apresentar os kits pra te ajudar a escolher o mais ideal — com segurança e economia."  

Apresentar os kits com foco em resultado  
Sempre apresente todos os 4 kits nesta ordem: 120 peças → 60 peças → 30 peças → 20 peças.  
Inclua os preços corretos, destaque que o de 30 peças é o mais vendido (por render certinho 1 mês) e compare de forma consultiva os benefícios.  
Nunca omita nenhum dos kits.  

Sugira o de 30 peças como primeira opção, com uma fala amigável e sincera, como se fosse de uma amiga que quer ajudar.  
Se a pessoa demonstrar preferência pelo de 20 peças, acolha com leveza e siga o atendimento normalmente.  

Destaque custo-benefício com frases como:  
"Esse costuma trazer resultado mais rápido pra quem sente esse tipo de dor."  

Comece pelo mais completo, mas adapte à realidade da pessoa  

Quando o cliente demonstrar interesse, conduza com uma sugestão sincera baseada em experiência:  
"Se for pra te dar uma dica sincera: o de 30 costuma ser o mais escolhido por quem tá começando. Ele rende certinho pra 1 mês de uso — que é o tempo ideal pra começar a sentir o efeito com mais clareza."  
"Mas se a dor estiver mais intensa ou se quiser garantir um tempo maior de uso, os maiores costumam aliviar mais rápido e compensam mais no valor por unidade."  

Se a pessoa quiser o de 20 mesmo assim, acolha com naturalidade:  
"Claro! O importante é a gente começar de algum jeito, né? 💙 Bora organizar certinho pra você já garantir o seu."  

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

🚫 NUNCA finalize perguntas com frases passivas ou abertas demais:
- "Se tiver dúvidas, estou à disposição"
- "Me chama se quiser"
- "Qualquer coisa, estou por aqui"
✅ Sempre conduza com pergunta direta e clara, para manter a conversa fluindo com segurança. 

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
Pausa estratégica:  
"Antes de organizarmos o pedido, ficou alguma dúvida que eu possa esclarecer pra te deixar mais segura?"  

Se estiver tudo certo, colete os dados em etapas curtas:  
✅ 1. Coleta de Dados Pessoais  
Bloco 1:  
"Perfeito! Vamos garantir seu pedido com segurança."  
Bloco 2:  
"Para começar, vou precisar de alguns dados seus:  
- Nome completo:  
- CPF:  
- Telefone com DDD:"  
Bloco 3:  
"Apresenta algum e-mail para envio do código de rastreio?"  

📍 2. Coleta de Endereço  
(Enviada após o cliente responder os dados pessoais)  
Bloco 1:  
"Agora, vamos precisar do seu endereço completo:  
- CEP:  
- Endereço completo:  
- Número:  
- Complemento (opcional):"  
Bloco 2:  
"Assim que tiver tudo certinho, seguimos com a finalização do pedido."  

Pergunte a forma de pagamento:  
"Perfeito! Prefere Pix à vista com desconto ou cartão em até 12x?"  

Envio da chave Pix — formato validado (em blocos curtos):  
Bloco 1:  
"Excelente! Abaixo, vou te passar a chave Pix (CNPJ) pra gente garantir o seu pedido com agilidade e segurança, tudo bem?"  
Bloco 2:  
52.940.645/0001-08  
Bloco 3:  
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

Produto:  
"O Flexlive é um adesivo com ingredientes naturais (mentol, cânfora, gengibre e absinto), que transportam compostos anti-inflamatórios direto pra área afetada, aliviando a dor, reduzindo o inchaço e recuperando a mobilidade."  

💖 FINALIDADE  
Graziela não vende produto. Ela transforma realidades.  
Ela escuta, entende, recomenda e conduz com intenção.  
Cada conversa é uma chance de devolver mobilidade e bem-estar. A venda é a consequência. A transformação é o objetivo.  
🌟 Lembre-se: cada conversa pode ser a virada de chave para alguém voltar a andar, a trabalhar ou simplesmente viver com mais dignidade. Conduza com o coração, a clareza e a presença que a situação merece."""
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

def analisar_estado_comportamental(mensagem, tentativas=1, followup_em_aberto=False):
    mensagem = mensagem.lower()

    # 🏷️ Etiqueta (Status Comercial)
    if tentativas >= 18 or any(frase in mensagem for frase in ["não quero mais", "cancela", "desiste", "quero cancelar"]):
        etiqueta = "Venda perdida"
    elif any(p in mensagem for p in ["comprovante", "paguei", "tá pago", "já fiz o pix", "enviei o pagamento"]):
        etiqueta = "Venda feita"
    elif any(p in mensagem for p in ["me chama", "às", "as ", "dia", "horário", "horas", "às ", "as ", "amanhã", "depois das", "semana que vem"]):
        etiqueta = "Agendado"
    elif "valor" in mensagem or "preço" in mensagem or "quanto custa" in mensagem:
        etiqueta = "Em negociação"
    elif any(p in mensagem for p in ["como funciona", "é eficaz", "tem efeito", "funciona mesmo", "qual a diferença", "ajuda com dor", "qual o benefício", "é bom"]):
        etiqueta = "Interessado"
    else:
        etiqueta = "em atendimento"

    # 🔍 Nível de Consciência
    if any(p in mensagem for p in ["o que é isso", "pra que serve", "me explica melhor", "nunca ouvi falar", "minha mãe que mandou", "só vi o anúncio", "tava só olhando", "não sei do que se trata"]):
        consciencia = "Inconsciente"
    if any(p in mensagem for p in ["dói muito", "dor no", "minha dor", "tá doendo", "não consigo andar", "não consigo dormir",  "tô cansado dessa dor", "essa dor me atrapalha", "uso remédio todo dia", "já tentei várias coisas"]):
        consciencia = "Consciente da dor"
    elif any(p in mensagem for p in ["já tentei de tudo", "nada funciona", "nada resolve", "já usei isso", "já comprei", "não resolveu"]):
        consciencia = "Consciente da solução"
    elif any(p in mensagem for p in ["Tenho interesse", "quero o flexlive", "quero o de 30", "qual o melhor kit", "me manda o link", "prefiro pix", "qual a diferença dos kits", "tem o de 60 peças"]):
        consciencia = "Consciente do produto"
    elif any(p in mensagem for p in ["já fiz o pix", "pode fechar", "quero fechar hoje", "meu cpf é", "vou querer o de 120",  "pode mandar", "quero garantir o meu", "vou comprar agora"]):
        consciencia = "Pronto para compra"
    else:
        consciencia = "Neutro"

    # 🙅 Objeções
    if any(p in mensagem for p in ["caro", "muito caro", "tá caro", "sem dinheiro", "não posso pagar", "desconto", "tem mais barato", "valor alto", "muito alto", "difícil pra mim agora"]):
        objecao = "Preço"
    elif any(p in mensagem for p in ["funciona mesmo", "parece golpe", "tem garantia", "é seguro", "parece mentira",  "não acredito", "é confiável", "não confio", "medo de comprar", "tem registro",  "tenho receio", "parece arriscado", "já fui enganado", "não conheço a empresa"]):
        objecao = "Confiança"
    elif any(p in mensagem for p in ["vou pensar", "depois eu vejo", "te chamo mais tarde", "vou falar com meu marido",  "ainda não sei", "talvez", "estou indecisa", "estou em dúvida", "quem sabe depois",  "mais pra frente", "agora não dá", "depois eu volto", "vou decidir ainda"]):
        objecao = "Indecisão"
    elif any(p in mensagem for p in ["não posso", "não quero", "não me interessa", "não serve pra mim", "não preciso",  "não ajuda", "já estou tratando", "não tenho dor", "já uso outro", "não vejo necessidade",  "já resolvi meu problema", "não uso essas coisas"]):
        objecao = "Necessidade"
    else:
        objecao = "Nenhuma aparente"

    return {
        "consciencia": consciencia,
        "objeção": objecao,
        "etiqueta": etiqueta
    }

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
            resumo = f"{resumo}\n{novo_resumo}".strip()
            mensagens = mensagens[-6:]
            print("📉 Mensagens antigas resumidas.")

        followup_em_aberto = etapa in ["aguardando_pagamento", "agendado", "pergunta_forma_pagamento"]
        estado = analisar_estado_comportamental(mensagem, tentativas, followup_em_aberto)
 
        doc_ref.set({
            "telefone": telefone,
            "etapa": etapa,
            "ultima_interacao": agora,
            "mensagens": mensagens,
            "resumo": resumo,
            "ultimo_resumo_em": agora.isoformat(),
            "last_msg_id": msg_id,
            "tentativas": tentativas,
            "nivel_consciencia": estado["consciencia"],
            "objecao_atual": estado["objeção"],
            "etiqueta": estado["etiqueta"]
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
            contexto = f"{resumo}\n" + "\n".join(linhas) if resumo else "\n".join(linhas)

            # Pega emojis já usados nas últimas mensagens da Graziela
            texto_respostas = " ".join([m["texto"] for m in mensagens if m["quem"] == "graziela"])
            emojis_ja_usados = [e for e in ["😊", "💙"] if e in texto_respostas]

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

def identificar_proxima_etapa(resposta_lower):
    if any(p in resposta_lower for p in [
        "imagino o quanto", "isso impacta", "entendo demais", "pesado conviver", "Vamos juntas"
        "vamos juntas encontrar", "diz muito sobre você", "abrir mão disso", "deve ser difícil conviver"
    ]):
        return "momento_conexao"
    
    elif any(p in resposta_lower for p in [
        "com base no que você compartilhou", "posso te mostrar os kits",
        "vou te apresentar as opções", "valores são", "kit mais vendido", "custam", "valor", "preço", "quanto custa", "tem desconto"
    ]):
        return "apresentando_preço"
    
    elif any(p in resposta_lower for p in [
        "vou precisar dos seus dados", "preciso de algumas informações suas",
        "pra garantir seu pedido", "vamos garantir seu pedido", "dados pessoais", "nome completo", "cpf", "telefone com ddd"
    ]):
        return "coletando_dados_pessoais"
    
    elif any(p in resposta_lower for p in [
        "vamos precisar do seu endereço", "endereço completo", "cep", "número", "bairro", "complemento (opcional)"
    ]):
        return "coletando_endereco"
    
    elif any(p in resposta_lower for p in [
        "prefere pix", "cartão em até 12x", "forma de pagamento", "como prefere pagar"
    ]):
        return "metodo_pagamento"
    
    elif any(p in resposta_lower for p in [
        "vou te passar a chave pix", "chave pix (cnpj)", "abaixo segue a chave", "para garantir seu pedido via pix"
    ]):
        return "aguardando_pagamento"
    
    elif any(p in resposta_lower for p in [
        "me envia o comprovante", "confirmar rapidinho no sistema", "envia aqui o pagamento", "assim consigo confirmar"
    ]):
        return "pagamento_confirmado"
    
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

    if etapa in ["momento_conexao"]:
        prompt.append({"role": "user", "content": f"""Nova mensagem do cliente:
{mensagem_completa}

IMPORTANTE:
Comece acolhendo com força emocional e conexão genuína. Demonstre escuta ativa e gere segurança com empatia.  
**Não apresente preços diretamente ainda.**  
Primeiro, crie valor e reforce como o Flexlive pode aliviar essa dor de forma leve e segura.

Conduza com frases como:
- "Nossa, entendo demais. Imagino o quanto deve estar pesado conviver com isso há tanto tempo."
- "Se for pra investir em algo, que seja no que pode devolver sua qualidade de vida, né?"
- "A gente só valoriza quando volta a andar sem dor."

Apenas **ao final**, conduza de forma sutil para apresentar os kits (em até 3 frases curtas por bloco, separadas por duas quebras de linha \\n\\n), com foco em solução leve e consciente.

⚠️ NUNCA use frases passivas como:
- "Se tiver dúvidas, estou à disposição."
- "Me chama se quiser."
- "Qualquer coisa, estou por aqui."
Essas frases enfraquecem a condução. Você deve sempre terminar com uma pergunta clara, direcionando o próximo passo da conversa."""})

    if etapa == "apresentando_preço":
        prompt.append({"role": "user", "content": f"""Nova mensagem do cliente:
{mensagem_completa}

IMPORTANTE: Não apresentar preço se ainda não tiver gerado valor! Concorde com o cliente, acolha com empatia e segurança emocional.  
Mostre que você entendeu o que ele sente e que o foco é aliviar essa dor com responsabilidade.

⚠️ Use no máximo 3 frases curtas por bloco, com até 350 caracteres cada.  
Separe os blocos com **duas quebras de linha (`\\n\\n`)** para simular uma conversa natural no WhatsApp.  
**Sempre inclua o kit de 120 peças.**

⚠️ NUNCA use frases passivas como:
- "Se tiver dúvidas, estou à disposição."
- "Me chama se quiser."
- "Qualquer coisa, estou por aqui."
Essas frases enfraquecem a condução. Você deve sempre terminar com uma pergunta clara, direcionando o próximo passo da conversa."""})

    elif etapa == "coletando_dados_pessoais":
        prompt.append({"role": "user", "content": f"""Nova mensagem do cliente:
{mensagem_completa}

IMPORTANTE: O cliente demonstrou que quer fechar o pedido. Agora, conduza com leveza a coleta dos dados pessoais em blocos curtos e claros:

Bloco 1:
"Perfeito! Vamos garantir seu pedido com segurança."

Bloco 2:
"Para começar, vou precisar de alguns dados seus:

- Nome completo:
- CPF:
- Telefone com DDD:"

Bloco 3:
"Apresenta algum e-mail para envio do código de rastreio?"

⚠️ NUNCA use frases passivas como:
- "Se tiver dúvidas, estou à disposição."
- "Me chama se quiser."
- "Qualquer coisa, estou por aqui."
Essas frases enfraquecem a condução. Você deve sempre terminar com uma pergunta clara, direcionando o próximo passo da conversa."""})

    elif etapa == "coletando_endereco":
        prompt.append({"role": "user", "content": f"""Nova mensagem do cliente:
{mensagem_completa}

IMPORTANTE: O cliente já passou os dados pessoais. Agora peça com gentileza os dados de endereço.

Bloco 1:
"Agora, vamos precisar do seu endereço completo:

- CEP:
- Endereço completo:
- Número:
- Complemento (opcional):"

Bloco 2:
"Assim que tiver tudo certinho, seguimos com a finalização do pedido."

⚠️ NUNCA use frases passivas como:
- "Se tiver dúvidas, estou à disposição."
- "Me chama se quiser."
- "Qualquer coisa, estou por aqui."
Essas frases enfraquecem a condução. Você deve sempre terminar com uma pergunta clara, direcionando o próximo passo da conversa."""})

    elif etapa == "metodo_pagamento":
        prompt.append({"role": "user", "content": f"""Nova mensagem do cliente:
{mensagem_completa}

IMPORTANTE: O cliente já passou os dados e demonstrou que quer finalizar a compra.

Agora, conduza com leveza e segurança:

**\"Prefere Pix à vista com desconto ou cartão em até 12x?\"**

Aguarde a resposta antes de enviar links ou instruções de pagamento.

⚠️ NUNCA use frases passivas como:
- "Se tiver dúvidas, estou à disposição."
- "Me chama se quiser."
- "Qualquer coisa, estou por aqui."
Essas frases enfraquecem a condução. Você deve sempre terminar com uma pergunta clara, direcionando o próximo passo da conversa.
"""})

    else:
        prompt.append({"role": "user", "content": f"""Nova mensagem do cliente:
{mensagem_completa}

IMPORTANTE: Estruture sua resposta em **blocos de até 3 frases curtas**, com no máximo 350 caracteres por bloco. Separe os blocos com **duas quebras de linha (`\\n\\n`)**.

Assim consigo entregar sua resposta no WhatsApp de forma mais natural, simulando uma conversa real.

⚠️ NUNCA use frases passivas como:
- "Se tiver dúvidas, estou à disposição."
- "Me chama se quiser."
- "Qualquer coisa, estou por aqui."
Essas frases enfraquecem a condução. Você deve sempre terminar com uma pergunta clara, direcionando o próximo passo da conversa.
"""})

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

    resposta_normalizada = re.sub(r'(\\n|\\r|\\r\\n|\r\n|\r|\n)', '\n', resposta)
    blocos, tempos = quebrar_em_blocos_humanizado(resposta_normalizada, limite=350)
    resposta_compacta = "\n\n".join(blocos)

    etapas_delay = {
        "coletando_dados_pessoais": 120,
        "coletando_endereco": 120,
        "pagamento_realizado": 25,
        "aguardando_pagamento": 30
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
