from fluxo.etapas_jornada import identificar_etapa_jornada
from fluxo.objecoes import identificar_objecao
from fluxo.consciencia_cliente import classificar_consciencia
from fluxo.temperatura import classificar_temperatura
from fluxo.ambiguidade import detectar_sinais_ambiguidade

# Ordem evolutiva dos níveis de consciência
NIVEIS_CONSCIENCIA = [
    "inconsciente",
    "problema_consciente",
    "solucao_consciente",
    "produto_consciente",
    "pronto_para_compra"
]

def objeção_foi_contornada(ultima_objeção: str, contexto: str) -> bool:
    if not ultima_objeção:
        return True

    texto = contexto.lower()
    sinais_positivos = ["entendi", "faz sentido", "vou comprar", "ok", "beleza"]
    sinais_de_troca = ["mudando de assunto", "seguinte", "outra coisa"]

    if any(s in texto for s in sinais_positivos + sinais_de_troca):
        return True

    return ultima_objeção.lower() not in texto

def avaliar_evolucao_consciencia(nova: str, anterior: str) -> str:
    if not nova:
        return anterior
    if not anterior:
        return nova

    try:
        idx_nova = NIVEIS_CONSCIENCIA.index(nova)
        idx_antiga = NIVEIS_CONSCIENCIA.index(anterior)
        return nova if idx_nova > idx_antiga else anterior
    except ValueError:
        return anterior

def controlar_jornada(mensagem: str, contexto: str, estado_anterior: dict = None) -> dict:
    texto_total = f"{contexto} {mensagem}".strip().lower()

    etapa, justificativa_etapa = identificar_etapa_jornada(texto_total)
    objecao, justificativa_objecao = identificar_objecao(texto_total)
    consciencia, justificativa_consciencia = classificar_consciencia(texto_total)
    temperatura, justificativa_temperatura = classificar_temperatura(mensagem)
    ambiguidade_detectada, justificativa_ambiguidade = detectar_sinais_ambiguidade(mensagem)

    if estado_anterior:
        if not ambiguidade_detectada and etapa:
            etapa_atual = etapa
            justificativa_etapa_atual = justificativa_etapa
        else:
            etapa_atual = estado_anterior.get("etapa")
            justificativa_etapa_atual = estado_anterior.get("justificativa_etapa")

        objecao_anterior = estado_anterior.get("objeção")
        if objecao_anterior and objeção_foi_contornada(objecao_anterior, texto_total):
            objecao_atual = None
            justificativa_objecao_atual = None
        else:
            objecao_atual = objecao or objecao_anterior
            justificativa_objecao_atual = justificativa_objecao or estado_anterior.get("justificativa_objecao")

        consciencia_atual = avaliar_evolucao_consciencia(consciencia, estado_anterior.get("consciência"))
        justificativa_consciencia_atual = justificativa_consciencia or estado_anterior.get("justificativa_consciencia")

        temperatura_atual = temperatura or estado_anterior.get("temperatura")
        justificativa_temperatura_atual = justificativa_temperatura or estado_anterior.get("justificativa_temperatura")

    else:
        etapa_atual = etapa
        justificativa_etapa_atual = justificativa_etapa
        objecao_atual = objecao
        justificativa_objecao_atual = justificativa_objecao
        consciencia_atual = consciencia
        justificativa_consciencia_atual = justificativa_consciencia
        temperatura_atual = temperatura
        justificativa_temperatura_atual = justificativa_temperatura

    return {
        "etapa": etapa_atual,
        "justificativa_etapa": justificativa_etapa_atual,
        "objeção": objecao_atual,
        "justificativa_objecao": justificativa_objecao_atual,
        "consciência": consciencia_atual,
        "justificativa_consciencia": justificativa_consciencia_atual,
        "temperatura": temperatura_atual,
        "justificativa_temperatura": justificativa_temperatura_atual,
        "ambiguidade": ambiguidade_detectada,
        "justificativa_ambiguidade": justificativa_ambiguidade
    }
