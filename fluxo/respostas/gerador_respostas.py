import re
from fluxo.servicos.openai_client import gerar_resposta
from fluxo.etapas_jornada import ETAPAS_JORNADA

FRASES_PROIBIDAS = [
    "se tiver dúvidas, estou à disposição",
    "me chama se quiser",
    "qualquer coisa, estou por aqui"
]

def contem_frase_proibida(texto):
    texto_lower = texto.lower()
    return any(frase in texto_lower for frase in FRASES_PROIBIDAS)

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

def gerar_resposta_formatada(prompt, emojis_ja_usados):
    resposta = gerar_resposta(prompt)
    if not resposta:
        return None, []

    resposta, novos_emojis = remover_emojis_repetidos(resposta, emojis_ja_usados)

    if contem_frase_proibida(resposta):
        print("⚠️ Frase passiva detectada. Solicitando reformulação automática.")
        reformulacao_prompt = [
            {"role": "system", "content": "Você é Graziela, consultora da Sportech. Reformule a mensagem anterior."},
            {"role": "user", "content": f"""Essa foi a resposta que você deu:

{resposta}

⚠️ Ela termina com uma frase passiva que não conduz a conversa.

Reescreva com tom gentil, mas encerrando com uma pergunta clara que incentive a continuidade da conversa.

Blocos curtos (máx. 350 caracteres) separados por duas quebras de linha."""}
        ]
        nova_resposta = gerar_resposta(reformulacao_prompt, temperatura=0.4)
        if nova_resposta:
            resposta, novos_emojis = remover_emojis_repetidos(nova_resposta, emojis_ja_usados)

    return resposta, novos_emojis
