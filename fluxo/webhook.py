from flask import Blueprint, request, make_response
import os
import json
from datetime import datetime

from fluxo.servicos.processador import iniciar_processamento
from fluxo.servicos.firestore import firestore_client
from google.cloud import firestore

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
    try:
        data = request.get_json()
        msg_data = data["entry"][0]["changes"][0]["value"]
        mensagens = msg_data.get("messages", [])
        if not mensagens:
            return "ok", 200

        telefone = mensagens[0].get("from")
        msg_id = mensagens[0].get("id")
        texto = mensagens[0].get("text", {}).get("body", "")

        temp_ref = firestore_client.collection("conversas_temp").document(telefone)
        temp_doc = temp_ref.get()
        pendentes = temp_doc.to_dict().get("pendentes", []) if temp_doc.exists else []

        pendentes.append({
            "texto": texto,
            "timestamp": datetime.utcnow().isoformat(),
            "msg_id": msg_id
        })

        temp_ref.set({"pendentes": pendentes})
        print("⏳ Mensagem adicionada à fila temporária.")

        iniciar_processamento(telefone)

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
