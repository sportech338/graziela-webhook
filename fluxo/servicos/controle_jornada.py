from fluxo.etapas_jornada import identificar_etapa_jornada
from fluxo.objecoes import identificar_objecao
from fluxo.consciencia_cliente import classificar_consciencia


def controlar_jornada(mensagem: str, estado_anterior: dict = None) -> dict:
    """
    Função central de controle da jornada do lead.
    Recebe a mensagem atual e o estado anterior (se existir),
    e retorna um novo estado atualizado com base na lógica de evolução.
    """
    nova_etapa = identificar_etapa_jornada(mensagem)
    nova_objecao = identificar_objecao(mensagem)
    nova_consciencia = classificar_consciencia(mensagem)

    estado_atualizado = {
        "etapa": nova_etapa or (estado_anterior.get("etapa") if estado_anterior else None),
        "objeção": nova_objecao or (estado_anterior.get("objeção") if estado_anterior else None),
        "consciência": nova_consciencia or (estado_anterior.get("consciência") if estado_anterior else None)
    }

    # 💡 Aqui no futuro podemos inserir lógica de progressão:
    # - Se lead respondeu X, avança etapa
    # - Se objeção desaparece, limpa objeção
    # - Se consciência muda, atualiza

    return estado_atualizado
