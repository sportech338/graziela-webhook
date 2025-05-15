import os
import time
import re
import threading
import requests
from datetime import datetime

from fluxo.servicos.firestore import (
    firestore_client,
    salvar_no_firestore,
    obter_contexto
)
from fluxo.servicos.sheets import registrar_no_sheets
from fluxo.servicos.openai_client import gerar_resposta
from fluxo.respostas.gerador_respostas import gerar_resposta_formatada, montar_prompt_por_etapa
from fluxo.base_prompt import BASE_PROMPT
from fluxo.servicos.controle_jornada import controlar_jornada
from fluxo.servicos.util import quebrar_em_blocos_humanizado

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
    mensagem_completa = " ".join([m["texto"] for m in mensagens_ordenadas if m.get("texto")]).strip()
    msg_id = mensagens_ordenadas[-1].get("msg_id")

    contexto, emojis_ja_usados = obter_contexto(telefone)
    estado_anterior = firestore_client.collection("conversas").document(telefone).get().to_dict() or {}

    estado_atual = controlar_jornada(mensagem_completa, contexto, estado_anterior)

    prompt = montar_prompt_por_etapa(
        etapa=estado_atual["etapa"],
        mensagem_cliente=mensagem_completa,
        contexto=contexto,
        base_prompt=BASE_PROMPT,
        objecao=estado_atual.get("objeção"),
        justificativa_objecao=estado_atual.get("justificativa_objecao"),
        ambiguidade_justificativa=estado_atual.get("justificativa_ambiguidade"),
        justificativa_consciencia=estado_atual.get("justificativa_consciencia"),
        justificativa_temperatura=estado_atual.get("justificativa_temperatura"),
        justificativa_etapa=estado_atual.get("justificativa_etapa")
    )

    resposta, novos_emojis = gerar_resposta_formatada(prompt, emojis_ja_usados)
    if not resposta:
        print("❌ Erro ao gerar resposta. Abortando.")
        return

    # Separa a resposta para cliente do bloco de dados
    partes = resposta.strip().rsplit("---", maxsplit=1)
    mensagem_cliente_final = partes[0].strip()
    bloco_dados = partes[1].strip() if len(partes) > 1 else ""

    etapa = estado_atual["etapa"]
    consciencia = estado_atual.get("consciência")
    temperatura = estado_atual.get("temperatura")
    objecao = estado_atual.get("objeção")
    ambiguidade = estado_atual.get("ambiguidade")

    for linha in bloco_dados.splitlines():
        if linha.lower().startswith("etapa:"):
            etapa = linha.split(":", 1)[1].strip()
        elif linha.lower().startswith("consciência:"):
            consciencia = linha.split(":", 1)[1].strip()
        elif linha.lower().startswith("temperatura:"):
            temperatura = linha.split(":", 1)[1].strip()
        elif linha.lower().startswith("objeção:"):
            objecao = linha.split(":", 1)[1].strip()
        elif linha.lower().startswith("ambiguidade:"):
            ambiguidade = linha.split(":", 1)[1].strip().lower() == "true"

    blocos, tempos = quebrar_em_blocos_humanizado(mensagem_cliente_final, etapa=etapa)
    resposta_compacta = "\n\n".join(blocos)

    sucesso = salvar_no_firestore(
        telefone=telefone,
        mensagem_cliente=mensagem_completa,
        resposta_ia=resposta_compacta,
        msg_id=msg_id,
        etapa_jornada=etapa,
        objecao=objecao,
        consciencia=consciencia,
        temperatura=temperatura,
        justificativa_objecao=estado_atual.get("justificativa_objecao"),
        justificativa_consciencia=estado_atual.get("justificativa_consciencia"),
        justificativa_temperatura=estado_atual.get("justificativa_temperatura"),
        justificativa_etapa=estado_atual.get("justificativa_etapa"),
        justificativa_ambiguidade=estado_atual.get("justificativa_ambiguidade")
    )

    if not sucesso:
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
    print("🩹 Fila temporária limpa.")
    print("🔁 Thread finalizada e status limpo.")
