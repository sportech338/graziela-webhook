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
    """Verifica se a objeção anterior ainda está presente no contexto atual."""
    if not ultima_objeção:
        return True

    texto = contexto.lower()
    sinais_positivos = ["entendi", "faz sentido", "vou comprar", "ok", "beleza"]
    sinais_de_troca = ["mudando de assunto", "seguinte", "outra coisa"]

    if any(s in texto for s in sinais_positivos + sinais_de_troca):
        return True

    return ultima_objeção.lower() not in texto

def avaliar_evolucao_consciencia(nova: str, anterior: str) -> str:
    """Garante que o nível de consciência só evolua, nunca regrida."""
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
    Controla a jornada do lead considerando a mensagem, o contexto e o estado anterior.
    Analisa consciência, objeção, temperatura, etapa e ambiguidade.
    """
    texto_total = f"{contexto} {mensagem}".strip().lower()
    sinais = detectar_sinais_ambiguidade(mensagem, contexto)

    nova_etapa = identificar_etapa_jornada(texto_total)
    nova_objecao = identificar_objecao(texto_total)
    nova_consciencia = classificar_consciencia(texto_total)
    nova_temperatura = classificar_temperatura(mensagem, contexto)

    if estado_anterior:
        # Só avança etapa se não houver ambiguidade
        etapa = estado_anterior.get("etapa")
        if not sinais["ambiguidade"] and nova_etapa:
            etapa = nova_etapa

        # Objeção: remove se foi contornada, senão mantém ou atualiza
        objecao_anterior = estado_anterior.get("objeção")
        if objecao_anterior and objeção_foi_contornada(objecao_anterior, texto_total):
            objecao = None
        else:
            objecao = nova_objecao or objecao_anterior

        # Consciência e temperatura são atualizadas com base em evolução
        consciencia = avaliar_evolucao_consciencia(nova_consciencia, estado_anterior.get("consciência"))
        temperatura = nova_temperatura or estado_anterior.get("temperatura")
    else:
        etapa = nova_etapa
        objecao = nova_objecao
        consciencia = nova_consciencia
        temperatura = nova_temperatura

    return {
        "etapa": etapa,
        "objeção": objecao,
        "consciência": consciencia,
        "temperatura": temperatura,
        "ambiguidade": sinais["ambiguidade"]  # 👀 pode ser usado no prompt ou na lógica de resposta
    }
