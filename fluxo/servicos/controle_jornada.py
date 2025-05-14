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
    ambiguidade_justificativa: Optional[str] = None,
    justificativa_etapa: Optional[str] = None,
    consciencia: Optional[str] = None,
    justificativa_consciencia: Optional[str] = None,
    temperatura: Optional[str] = None,
    justificativa_temperatura: Optional[str] = None
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
            "content": f"⚠️ Atenção: Pode haver ambiguidade, dúvida ou ironia na última mensagem.\n\n{ambiguidade_justificativa}\n\nUse o histórico para validar se é o caso e responda de forma empática e clara."
        })

    if objecao:
        justificativa_txt = f"\n\nContexto adicional: {justificativa_objecao}" if justificativa_objecao else ""
        prompt.append({
            "role": "user",
            "content": f"⚠️ Objeção detectada: {objecao.replace("_", " ").capitalize()}.{justificativa_txt}\n\nAntes de seguir normalmente, contorne a objeção com empatia, prova social e reforço de confiança.\n\nSó depois retome o fluxo com condução leve e consultiva.\n\n⚠️ Use blocos curtos (máx. 350 caracteres), com duas quebras de linha entre eles."
        })

    if etapa:
        justificativa_etapa_txt = f"\nJustificativa da etapa sugerida: {justificativa_etapa}" if justificativa_etapa else ""
        prompt.append({
            "role": "user",
            "content": f"Etapa sugerida: {etapa}.{justificativa_etapa_txt}"
        })

    if consciencia:
        justificativa_consciencia_txt = f"\nJustificativa da consciência sugerida: {justificativa_consciencia}" if justificativa_consciencia else ""
        prompt.append({
            "role": "user",
            "content": f"Nível de consciência sugerido: {consciencia}.{justificativa_consciencia_txt}"
        })

    if temperatura:
        justificativa_temperatura_txt = f"\nJustificativa da temperatura sugerida: {justificativa_temperatura}" if justificativa_temperatura else ""
        prompt.append({
            "role": "user",
            "content": f"Temperatura do cliente: {temperatura}.{justificativa_temperatura_txt}"
        })

    prompt.append({
        "role": "user",
        "content": f"Nova mensagem do cliente:\n{mensagem_cliente}\n\nResponda com empatia, leveza e estratégia. Evite frases passivas. Finalize com uma pergunta clara que incentive a continuidade.\n\nBlocos curtos (máx. 350 caracteres), com quebras de linha se fizer sentido."
    })

    return prompt
