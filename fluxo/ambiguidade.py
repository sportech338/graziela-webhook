import re
from typing import Optional

# Padrões que podem indicar ironia ou sarcasmo
PADROES_IRONIA = [
    r"só que não", r"aham", r"sei\.\.\.", r"super empolgado", r"mal posso esperar",
    r"tá bom então", r"imagina", r"claro que sim", r"isso com certeza vai funcionar"
]

# Padrões que podem indicar dúvida disfarçada ou hesitação
PADROES_DUVIDA_DISFARCADA = [
    r"se funcionar", r"acho que sim", r"vou ver", r"depois eu vejo",
    r"qualquer coisa eu volto", r"vou pensar", r"não sei ainda"
]

def detectar_sinais_ambiguidade(mensagem: str, contexto: Optional[str] = "") -> dict:
    """
    Detecta sinais de ambiguidade na mensagem do lead, incluindo ironia e hesitação.

    Args:
        mensagem: Texto mais recente enviado pelo usuário.
        contexto: Histórico da conversa (opcional).

    Returns:
        dict: Flags booleanas para 'ironia', 'duvida' e 'ambiguidade'.
    """
    texto = f"{mensagem} {contexto}".lower()
    ironia = any(re.search(p, texto) for p in PADROES_IRONIA)
    duvida = any(re.search(p, texto) for p in PADROES_DUVIDA_DISFARCADA)
    return {
        "ironia": ironia,
        "duvida": duvida,
        "ambiguidade": ironia or duvida
    }
