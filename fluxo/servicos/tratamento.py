import os
import re
import time
import requests
from datetime import datetime
from collections import defaultdict

from fluxo.servicos.firestore import (
    firestore_client,
    obter_contexto,
    salvar_no_firestore
)
from fluxo.servicos.sheets import registrar_no_sheets
from fluxo.servicos.openai_client import gerar_resposta
from fluxo.servicos.audio import baixar_audio_do_meta, transcrever_audio
from fluxo.servicos.util import quebrar_em_blocos_humanizado, remover_emojis_repetidos

BASE_PROMPT = os.environ.get("BASE_PROMPT", "Você é Graziela...")  # ou importar de um arquivo separado

def processar_mensagem_recebida(data):
    mensagens = data["entry"][0]["changes"][0]["value"].get("messages", [])
    if not mensagens:
        print("⚠️ Nenhuma mensagem recebida.")
        return

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
            blob = baixar_audio_do_meta(msg["audio"]["id"])
            texto = transcrever_audio(blob) if blob else ""
            if texto:
                mensagens_por_remetente[telefone].append((timestamp, texto))

    if telefone not in mensagens_por_remetente:
        return

    # Junta as mensagens em uma só
    sorted_msgs = sorted(mensagens_por_remetente[telefone], key=lambda x: x[0])
    mensagem_completa = " ".join([txt for _, txt in sorted_msgs]).strip()

    # Determina a etapa com base no conteúdo
    etapa = detectar_etapa(mensagem_completa)

    # Monta prompt com histórico
    prompt = [{"role": "system", "content": BASE_PROMPT}]
    contexto, emojis_ja_usados = obter_contexto(telefone)
    if contexto:
        prompt.append({"role": "user", "content": f"Histórico da conversa:\n{contexto}"})
    else:
        emojis_ja_usados = []

    prompt.append({"role": "user", "content": mensagem_completa})

    # Chamada à OpenAI
    resposta = gerar_resposta(prompt)
    resposta, _ = remover_emojis_repetidos(resposta, emojis_ja_usados)
    resposta_normalizada = re.sub(r'(\\n|\\r|\\r\\n|\r\n|\r|\n)', '\n', resposta)
    blocos, tempos = quebrar_em_blocos_humanizado(resposta_normalizada, limite=350)

    # Salva no Firestore
    resposta_compacta = "\n\n".join(blocos)
    if not salvar_no_firestore(telefone, mensagem_completa, resposta_compacta, msg_id, etapa):
        return

    # Envia resposta no WhatsApp
    enviar_resposta_whatsapp(telefone, blocos, tempos)

    # Registra no Sheets
    registrar_no_sheets(telefone, mensagem_completa, resposta_compacta)

def detectar_etapa(texto):
    texto = texto.lower()
    if any(p in texto for p in ["paguei", "comprovante"]):
        return "pagamento_realizado"
    elif "pix" in texto or "transferência" in texto:
        return "aguardando_pagamento"
    elif all(p in texto for p in ["nome", "cpf", "telefone"]) and "email" in texto:
        return "coletando_dados_pessoais"
    elif all(p in texto for p in ["cep", "endereço", "número", "bairro", "cidade"]):
        return "coletando_endereco"
    elif any(p in texto for p in ["valor", "preço"]):
        return "solicitou_valor"
    elif any(p in texto for p in ["caro", "sem grana", "tá difícil"]):
        return "resistencia_financeira"
    return "inicio"

def enviar_resposta_whatsapp(telefone, blocos, tempos):
    url = f"https://graph.facebook.com/v18.0/{os.environ['PHONE_NUMBER_ID']}/messages"
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
        res = requests.post(url, headers=headers, json=payload)
        print(f"📤 Enviando bloco {i+1}: {res.status_code} | {res.text}")
        time.sleep(delay)
