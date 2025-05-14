from fluxo.etapas_jornada import identificar_etapa_jornada
from fluxo.objecoes import identificar_objecao
from fluxo.consciencia_cliente import classificar_consciencia
from fluxo.temperatura import classificar_temperatura

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

    etapa = identificar_etapa_jornada(texto_total)
    objecao = identificar_objecao(texto_total)
    consciencia = classificar_consciencia(texto_total)
    temperatura = classificar_temperatura(mensagem, contexto)

    if estado_anterior:
        etapa = etapa or estado_anterior.get("etapa")

        objecao_anterior = estado_anterior.get("objeção")
        if objecao_anterior and objeção_foi_contornada(objecao_anterior, texto_total):
            objecao = None
        else:
            objecao = objecao or objecao_anterior

        consciencia = avaliar_evolucao_consciencia(consciencia, estado_anterior.get("consciência"))
        temperatura = temperatura or estado_anterior.get("temperatura")

    return {
        "etapa": etapa,
        "objeção": objecao,
        "consciência": consciencia,
        "temperatura": temperatura
    }
