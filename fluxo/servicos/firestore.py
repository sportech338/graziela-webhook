from google.cloud import firestore
from datetime import datetime
import os
from fluxo.servicos.util import criar_arquivo_credenciais

CREDENTIALS_PATH = "credentials.json"

# 🔐 Garante que as credenciais estão disponíveis
if not os.path.exists(CREDENTIALS_PATH):
    criar_arquivo_credenciais(CREDENTIALS_PATH)

firestore_client = firestore.Client.from_service_account_json(CREDENTIALS_PATH)


def salvar_no_firestore(
    telefone: str,
    mensagem_cliente: str,
    resposta_ia: str,
    msg_id: str,
    etapa_jornada: str,
    objecao: str = None,
    consciencia: str = None,
    temperatura: str = None
) -> bool:
    try:
        print("📝 Iniciando salvamento no Firestore...")
        agora = datetime.now()
        doc_ref = firestore_client.collection("conversas").document(telefone)
        doc = doc_ref.get()

        if doc.exists:
            data = doc.to_dict()
            mensagens = data.get("mensagens", [])
            resumo = data.get("resumo", "")
        else:
            data = {}
            mensagens = []
            resumo = ""

        # ➕ Adiciona novas mensagens
        mensagens.append({
            "quem": "cliente",
            "texto": mensagem_cliente,
            "timestamp": agora.isoformat()
        })
        mensagens.append({
            "quem": "graziela",
            "texto": resposta_ia,
            "timestamp": agora.isoformat()
        })

        # ✂️ Resume se houver excesso de mensagens
        if len(mensagens) > 40:
            from fluxo.servicos.openai_client import resumir_texto
            texto_completo = "\n".join([
                f"{'Cliente' if m['quem'] == 'cliente' else 'Graziela'}: {m['texto']}"
                for m in mensagens
            ])
            novo_resumo = resumir_texto(texto_completo)
            resumo = f"{resumo}\n{novo_resumo}".strip()
            mensagens = mensagens[-6:]  # Mantém apenas as últimas

            print("📉 Mensagens antigas resumidas.")

        dados_salvos = {
            "telefone": telefone,
            "etapa": etapa_jornada,
            "ultima_interacao": agora,
            "mensagens": mensagens,
            "resumo": resumo,
            "ultimo_resumo_em": agora.isoformat(),
            "last_msg_id": msg_id,
            "objeção": objecao or data.get("objeção"),
            "consciência": consciencia or data.get("consciência"),
            "temperatura": temperatura or data.get("temperatura")
        }

        print("🧾 Dados que serão salvos:", dados_salvos)
        doc_ref.set(dados_salvos)

        print("📦 Mensagens salvas no Firestore com sucesso.")
        return True

    except Exception as e:
        print(f"❌ Erro ao salvar no Firestore: {e}")
        return False


def obter_contexto(telefone: str):
    try:
        doc = firestore_client.collection("conversas").document(telefone).get()
        if doc.exists:
            dados = doc.to_dict()
            resumo = dados.get("resumo", "")
            mensagens = dados.get("mensagens", [])

            linhas = [
                f"{'Cliente' if m['quem'] == 'cliente' else 'Graziela'}: {m['texto']}"
                for m in mensagens
            ]
            contexto = f"{resumo}\n" + "\n".join(linhas) if resumo else "\n".join(linhas)

            texto_respostas = " ".join(
                m["texto"] for m in mensagens if m["quem"] == "graziela"
            )
            emojis_ja_usados = [e for e in ["😊", "💙"] if e in texto_respostas]

            return contexto, emojis_ja_usados
    except Exception as e:
        print(f"❌ Erro ao obter contexto: {e}")
    return "", []
