from google.cloud import firestore
from datetime import datetime
from fluxo.servicos.resumo import resumir_historico

firestore_client = firestore.Client.from_service_account_json("credentials.json")

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
            texto_completo = "\n".join([
                f"{'Cliente' if m['quem']=='cliente' else 'Graziela'}: {m['texto']}" for m in mensagens
            ])
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
            contexto = f"{resumo}\n" + "\n".join(linhas) if resumo else "\n".join(linhas)

            texto_respostas = " ".join([m["texto"] for m in mensagens if m["quem"] == "graziela"])
            emojis_ja_usados = [e for e in ["😊", "💙"] if e in texto_respostas]

            return contexto, emojis_ja_usados
    except Exception as e:
        print(f"❌ Erro ao obter contexto: {e}")
    return "", []
