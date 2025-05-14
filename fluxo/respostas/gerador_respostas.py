import re
from typing import Optional
from fluxo.servicos.openai_client import gerar_resposta
from fluxo.etapas_jornada import ETAPAS_JORNADA

FRASES_PROIBIDAS = [
    "se tiver dúvidas, estou à disposição",
    "me chama se quiser",
    "qualquer coisa, estou por aqui"
]

def contem_frase_proibida(texto: str) -> bool:
    texto_lower = texto.lower()
    return any(frase in texto_lower for frase in FRASES_PROIBIDAS)

def remover_emojis_repetidos(texto: str, emojis_ja_usados: list[str]) -> tuple[str, list[str]]:
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

def gerar_resposta_formatada(prompt: list[dict], emojis_ja_usados: list[str]) -> tuple[Optional[str], list[str]]:
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

def montar_prompt_por_etapa(
    etapa: str,
    mensagem_cliente: str,
    contexto: str,
    base_prompt: str,
    objecao: Optional[str] = None,
    justificativa_objecao: Optional[str] = None,
    ambiguidade_justificativa: Optional[str] = None
) -> list[dict]:
    prompt = [{"role": "system", "content": base_prompt}]

    if contexto:
        prompt.append({
            "role": "user",
            "content": f"Histórico da conversa até aqui:\n{contexto}"
        })

    if ambiguidade_justificativa:
        prompt.append({
            "role": "user",
            "content": f"""⚠️ Atenção: Pode haver ambiguidade, dúvida ou ironia na última mensagem. 

{ambiguidade_justificativa}

Use o histórico para validar se é o caso e responda de forma empática e clara."""
        })

    if objecao:
        justificativa_txt = f"\n\nContexto adicional: {justificativa_objecao}" if justificativa_objecao else ""
        prompt.append({
            "role": "user",
            "content": f"""⚠️ Objeção detectada: {objecao.replace("_", " ").capitalize()}.{justificativa_txt}

Antes de seguir normalmente, contorne a objeção com empatia, prova social e reforço de confiança.

Só depois retome o fluxo com condução leve e consultiva.

⚠️ Use blocos curtos (máx. 350 caracteres), com duas quebras de linha entre eles."""
        })

    mensagem_base = f"Nova mensagem do cliente:\n{mensagem_cliente}"

    if etapa == "apresentou_valor":
        prompt.append({
            "role": "user",
            "content": mensagem_base + """

IMPORTANTE: Antes de apresentar os valores, acolha com empatia.  
Depois conduza para os kits (120 → 60 → 30 → 20).  
Destaque o de 30 como mais vendido.  
Finalize com pergunta consultiva clara.

Blocos curtos (máx. 350 caracteres), separados por duas quebras de linha."""
        })

    elif etapa == "coleta_dados_pessoais":
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
"Tem algum e-mail pra envio do código de rastreio?" """
        })

    elif etapa == "coleta_endereco":
        prompt.append({
            "role": "user",
            "content": mensagem_base + """

Agora solicite o endereço:

Bloco 1:
"Agora preciso do seu endereço completo:

- CEP:
- Endereço:
- Número:
- Complemento (opcional):"

Bloco 2:
"Assim que estiver certinho, seguimos pra finalização." """
        })

    elif etapa == "forma_pagamento":
        prompt.append({
            "role": "user",
            "content": mensagem_base + """

Cliente pronto pra fechar. Pergunte direto:

"Prefere Pix à vista com desconto ou cartão em até 12x?"

Aguarde a escolha antes de enviar qualquer link."""
        })

    else:
        prompt.append({
            "role": "user",
            "content": mensagem_base
        })

    prompt.append({
        "role": "user",
        "content": """Responda com leveza e empatia.

Se a resposta for longa, divida em blocos curtos de até 350 caracteres cada, separados por duas quebras de linha (\n\n), para facilitar a leitura.

Evite blocos desnecessários em respostas curtas. Só use quebras quando ajudar na clareza e no ritmo da conversa.

Finalize com uma pergunta consultiva que incentive a continuidade da interação."""
    })

    return prompt
