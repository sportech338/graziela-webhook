from flask import Blueprint, request, make_response
import os
import json
import time
from datetime import datetime
import threading
from collections import defaultdict

from fluxo.servicos.firestore import firestore_client
from fluxo.servicos.audio import baixar_audio_do_meta, transcrever_audio
from fluxo.servicos.sheets import registrar_no_sheets
from fluxo.respostas.gerador_respostas import gerar_resposta  # em breve vamos ajustar isso
from fluxo.etapas_jornada import ETAPAS_JORNADA

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/", methods=["GET"])
def home():
    return "Servidor da Graziela com memória ativa 💬🧠"


@webhook_bp.route("/webhook", methods=["GET"])
def verify_webhook():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == os.environ.get("VERIFY_TOKEN"):
        return make_response(request.args.get("hub.challenge"), 200)
    return make_response("Erro de verificação", 403)

@webhook_bp.route("/webhook", methods=["POST"])
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


@webhook_bp.route("/filtrar-etapa/<etapa>", methods=["GET"])
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

    resposta, etapa = gerar_resposta(telefone, mensagem_completa, msg_id)

    if not salvar_no_firestore(telefone, mensagem_completa, resposta, msg_id, etapa):
        return

    registrar_no_sheets(telefone, mensagem_completa, resposta)
    temp_ref.delete()
    firestore_client.collection("status_threads").document(telefone).delete()
    print("🧹 Fila temporária limpa.")
    print("🔁 Thread finalizada e status limpo.")

