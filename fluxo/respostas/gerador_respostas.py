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

def montar_prompt_por_etapa(etapa, mensagem_cliente, contexto, base_prompt):
    prompt = [
        {
            "role": "system",
            "content": base_prompt
        }
    ]

    if contexto:
        prompt.append({
            "role": "user",
            "content": f"Histórico da conversa até aqui:\n{contexto}"
        })

    mensagem_base = f"Nova mensagem do cliente:\n{mensagem_cliente}"

    if etapa == "solicitou_valor":
        prompt.append({
            "role": "user",
            "content": mensagem_base + """

IMPORTANTE: Antes de apresentar os valores, acolha com empatia. Só depois conduza para os kits (120 → 60 → 30 → 20). Destaque o de 30 como mais vendido. Finalize com pergunta consultiva clara.
Responda em blocos curtos (máx. 350 caracteres), separados por duas quebras de linha (\\n\\n)."""
        })

    elif etapa == "coletando_dados_pessoais":
        prompt.append({
            "role": "user",
            "content": mensagem_base + """

O cliente quer finalizar. Solicite dados pessoais com leveza:

Bloco 1:
"Perfeito! Vamos garantir seu pedido com segurança."

Bloco 2:
"Preciso de alguns dados seus:

- Nome completo:
- CPF:
- Telefone com DDD:"

Bloco 3:
"Tem algum e-mail pra envio do código de rastreio?"
"""
        })

    elif etapa == "coletando_endereco":
        prompt.append({
            "role": "user",
            "content": mensagem_base + """

O cliente já passou os dados. Agora, solicite o endereço:

"Agora preciso do seu endereço completo:

- CEP:
- Endereço:
- Número:
- Complemento (opcional):"

"Assim que estiver certinho, seguimos pra finalização."
"""
        })

    elif etapa == "resistencia_financeira":
        prompt.append({
            "role": "user",
            "content": mensagem_base + """

Acolha com empatia. Mostre valor antes de apresentar qualquer preço.

- \"Imagino o quanto deve estar pesado conviver com isso.\"
- \"Se for pra investir em algo, que seja no que pode devolver sua qualidade de vida, né?\"

Finalize com uma pergunta clara. Blocos curtos, tom consultivo."""
        })

    elif etapa == "pergunta_forma_pagamento":
        prompt.append({
            "role": "user",
            "content": mensagem_base + """

Cliente pronto pra fechar. Pergunte direto:

\"Prefere Pix à vista com desconto ou cartão em até 12x?\"

Nada de frases abertas. Aguarde a escolha antes de mandar link."""
        })

    else:
        prompt.append({
            "role": "user",
            "content": mensagem_base + """

Responda com empatia e leveza. Use blocos curtos (máx. 350 caracteres) e termine com uma pergunta clara que mantenha o fluxo. Nunca use frases passivas como 'qualquer coisa, estou por aqui'."""
        })

    return prompt
