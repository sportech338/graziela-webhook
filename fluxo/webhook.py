from flask import Blueprint, request, make_response
import os
import json

from fluxo.servicos.processador import processar_mensagem_recebida
from fluxo.servicos.firestore import salvar_no_firestore, obter_contexto, firestore_client

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
        processar_mensagem_recebida(request.get_json())
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
