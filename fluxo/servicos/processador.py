import os
import time
import re
import threading
import requests
from datetime import datetime

from fluxo.servicos.firestore import firestore_client, salvar_no_firestore, obter_contexto
from fluxo.servicos.sheets import registrar_no_sheets
from fluxo.servicos.openai_client import gerar_resposta
from fluxo.respostas.gerador_respostas import gerar_resposta_formatada, montar_prompt_por_etapa
from fluxo.base_prompt import BASE_PROMPT
from fluxo.etapas_jornada import identificar_etapa_jornada
from fluxo.objecoes import identificar_objecao
from fluxo.servicos.consciencia_cliente import classificar_consciencia

ETAPAS_DELAY = {
    "inicio": 15,
    "coletando_dados_pessoais": 120,
    "coletando_endereco": 120,
    "pagamento_realizado": 25,
    "aguardando_pagamento": 30,
    "resistencia_financeira": 20
}

def quebrar_em_blocos_humanizado(texto, limite=350):
    blocos, tempos = [], []
    for trecho in texto.split("\n\n"):
        trecho = trecho.strip()
        if not trecho:
            continue
        if len(trecho) <= limite:
            blocos.append(trecho)
        else:
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

    for i, bloco in enumerate(blocos):
        if i == 0:
            tempos.append(ETAPAS_DELAY.get("inicio", 15))
        elif len(bloco) > 250:
            tempos.append(6)
        elif len(bloco) > 100:
            tempos.append(4)
        else:
            tempos.append(2)
    return blocos, tempos


def iniciar_processamento(telefone):
    status_ref = firestore_client.collection("status_threads").document(telefone)
    doc = status_ref.get()

    if doc.exists and doc.to_dict().get("em_execucao"):
        print(f"⏳ Já existe uma thread ativa para {telefone}. Ignorando nova chamada.")
        return

    status_ref.set({"em_execucao": True})
    print(f"🚀 Iniciando nova thread para {telefone}.")
    threading.Thread(target=processar_mensagem_da_fila, args=(telefone,)).start()


def processar_mensagem_da_fila(telefone):
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

    etapa = identificar_etapa_jornada(mensagem_completa) or "abordagem_inicial"
    objecao = identificar_objecao(mensagem_completa)  # 👈 detecta objeção aqui
    consciencia = classificar_consciencia(mensagem_completa)
    contexto, emojis_ja_usados = obter_contexto(telefone)
    prompt = montar_prompt_por_etapa(etapa, mensagem_completa, contexto, BASE_PROMPT, objecao=objecao)

    resposta, novos_emojis = gerar_resposta_formatada(prompt, emojis_ja_usados)
    if not resposta:
        print("❌ Erro ao gerar resposta. Abortando.")
        return

    resposta_normalizada = re.sub(r'(\\n|\\r|\\r\\n|\r\n|\r|\n)', '\n', resposta)
    blocos, tempos = quebrar_em_blocos_humanizado(resposta_normalizada)
    resposta_compacta = "\n\n".join(blocos)

    # 👇 aqui passamos objecao como o 6º argumento
    if not salvar_no_firestore(telefone, mensagem_completa, resposta_compacta, msg_id, etapa, objecao):
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
        res = requests.post(whatsapp_url, headers=headers, json=payload)
        print(f"📤 Enviado bloco {i+1}/{len(blocos)}: {res.status_code} | {res.text}")
        time.sleep(delay)

    registrar_no_sheets(telefone, mensagem_completa, resposta_compacta)
    temp_ref.delete()
    firestore_client.collection("status_threads").document(telefone).delete()
    print("🧹 Fila temporária limpa.")
    print("🔁 Thread finalizada e status limpo.")
