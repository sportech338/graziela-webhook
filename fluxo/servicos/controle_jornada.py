from fluxo.etapas_jornada import identificar_etapa_jornada
from fluxo.objecoes import identificar_objecao
from fluxo.consciencia_cliente import classificar_consciencia

# Níveis ordenados de consciência
NIVEIS_CONSCIENCIA = [
    "inconsciente",
    "problema_consciente",
    "solucao_consciente",
    "produto_consciente",
    "pronto_para_compra"
]

def objeção_foi_contornada(ultima_objeção: str, contexto: str, mensagem: str) -> bool:
    if not ultima_objeção:
        return True
    texto = (contexto + " " + mensagem).lower()
    sinais_positivos = ["entendi", "faz sentido", "ok", "vou comprar", "tá bom", "beleza"]
    sinais_de_troca = ["mudando de assunto", "outra dúvida", "mas enfim", "seguinte"]
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
    """
    Controla a evolução do lead com base em mensagem + contexto + estado anterior.
    """
    nova_etapa = identificar_etapa_jornada(mensagem)
    nova_objecao = identificar_objecao(mensagem)
    nova_consciencia = classificar_consciencia(mensagem)

    etapa = nova_etapa or (estado_anterior.get("etapa") if estado_anterior else None)

    if estado_anterior:
        objecao_anterior = estado_anterior.get("objeção")
        if objecao_anterior and objeção_foi_contornada(objecao_anterior, contexto, mensagem):
            objecao = None
        else:
            objecao = nova_objecao or objecao_anterior
    else:
        objecao = nova_objecao

    consciencia_anterior = estado_anterior.get("consciência") if estado_anterior else None
    consciencia = avaliar_evolucao_consciencia(nova_consciencia, consciencia_anterior)

    return {
        "etapa": etapa,
        "objeção": objecao,
        "consciência": consciencia
    }
