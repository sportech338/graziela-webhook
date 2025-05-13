import threading
from fluxo.servicos.firestore import firestore_client
from fluxo.servicos.tratamento import tratar_mensagem  # vamos criar essa função também
from datetime import datetime

def processar_mensagem_recebida(data):
    try:
        mensagens = data["entry"][0]["changes"][0]["value"].get("messages", [])
        if not mensagens:
            print("⚠️ Nenhuma mensagem recebida.")
            return

        for msg in mensagens:
            telefone = msg.get("from")
            msg_id = msg.get("id")
            timestamp = datetime.utcnow().isoformat()
            texto = ""

            if msg.get("type") == "text":
                texto = msg["text"]["body"]
            elif msg.get("type") == "audio":
                from fluxo.servicos.audio import baixar_audio_do_meta, transcrever_audio
                blob = baixar_audio_do_meta(msg["audio"]["id"])
                texto = transcrever_audio(blob) if blob else ""

            if telefone and texto:
                temp_ref = firestore_client.collection("conversas_temp").document(telefone)
                temp_doc = temp_ref.get()
                pendentes = temp_doc.to_dict().get("pendentes", []) if temp_doc.exists else []

                pendentes.append({
                    "texto": texto,
                    "timestamp": timestamp,
                    "msg_id": msg_id
                })

                temp_ref.set({"pendentes": pendentes})
                print("⏳ Mensagem adicionada à fila temporária.")

                status_ref = firestore_client.collection("status_threads").document(telefone)
                if not status_ref.get().exists:
                    status_ref.set({"em_execucao": True})
                    threading.Thread(target=tratar_mensagem, args=(telefone,)).start()
    except Exception as e:
        print(f"❌ Erro ao processar mensagem recebida: {e}")
