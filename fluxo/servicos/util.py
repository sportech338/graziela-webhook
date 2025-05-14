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
    emojis_validos = ["😊", "💙", "😔"]
    novos_emojis_usados = []

    for emoji in emojis_validos:
        ocorrencias = [m.start() for m in re.finditer(re.escape(emoji), texto)]
        if emoji in emojis_ja_usados and ocorrencias:
            texto = texto.replace(emoji, "", len(ocorrencias))
        elif ocorrencias:
            texto = texto.replace(emoji, "", len(ocorrencias) - 1)
            novos_emojis_usados.append(emoji)

    return texto, novos_emojis_usados

def quebrar_em_blocos_humanizado(texto, etapa=None, limite=350):
    DELAY_POR_ETAPA = {
        "abordagem_inicial": 20,
        "conexao_profunda": 12,
        "entendimento_dor": 15,
        "antecipou_objecao": 12,
        "apresentou_produto": 10,
        "prova_social": 8,
        "apresentou_valor": 20,
        "reforco_beneficio_personalizado": 10,
        "validou_oferta": 8,
        "comparou_kits": 12,
        "verificou_duvidas": 6,
        "recomendacao_final_fechamento": 8,
        "confirmacao_resumo_pedido": 10,
        "coleta_dados_pessoais": 120,
        "coleta_endereco": 120,
        "forma_pagamento": 60,
        "aguardando_pagamento": 60,
        "pagamento_realizado": 25,
        "pos_venda": 15,
        "encerramento": 10,
        "reengajamento": 15,
        "recuperacao_fluxo": 15
    }

    blocos = []
    tempos = []

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
            if etapa not in DELAY_POR_ETAPA:
                print(f"⚠️ Etapa '{etapa}' não configurada em DELAY_POR_ETAPA. Usando delay padrão de 15s.")
            tempos.append(DELAY_POR_ETAPA.get(etapa, 15))
        elif len(bloco) > 250:
            tempos.append(6)
        elif len(bloco) > 100:
            tempos.append(4)
        else:
            tempos.append(2)

    return blocos, tempos

def debug_justificativas(**kwargs):
    print("\n🧠 Justificativas dos pilares:")
    for chave, valor in kwargs.items():
        if valor:
            print(f"- {chave}: {valor}")
