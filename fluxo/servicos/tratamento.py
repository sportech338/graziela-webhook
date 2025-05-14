import re

def quebrar_em_blocos_humanizado(texto, limite=350):
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
            tempos.append(15)
        elif len(bloco) > 250:
            tempos.append(6)
        elif len(bloco) > 100:
            tempos.append(4)
        else:
            tempos.append(2)

    return blocos, tempos


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
