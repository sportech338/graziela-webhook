import os
import base64
import re

def criar_arquivo_credenciais(caminho_arquivo="credentials.json", var_env="GOOGLE_CREDENTIALS_BASE64"):
    try:
        encoded = os.environ.get(var_env)
        if not encoded:
            raise ValueError(f"Variável {var_env} não encontrada.")
        decoded = base64.b64decode(encoded).decode("utf-8")
        with open(caminho_arquivo, "w") as f:
            f.write(decoded)
        print(f"🔐 Arquivo {caminho_arquivo} criado com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao criar {caminho_arquivo}: {e}")

def quebrar_em_blocos(texto, limite=350):
    blocos = []
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
    return blocos

def remover_emojis_repetidos(texto, emojis_ja_usados):
    emojis_validos = ["😊", "💙"]
    novos_emojis_usados = []

    for emoji in emojis_validos:
        ocorrencias = [m.start() for m in re.finditer(re.escape(emoji), texto)]
        if emoji in emojis_ja_usados and ocorrencias:
            texto = texto.replace(emoji, "", len(ocorrencias))
        elif ocorrencias:
            texto = texto.replace(emoji, "", len(ocorrencias) - 1)
            novos_emojis_usados.append(emoji)

    return texto, novos_emojis_usados
