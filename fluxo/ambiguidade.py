import re
from typing import Optional, Tuple

# Frases que geralmente indicam sarcasmo, ironia ou desdém
PADROES_IRONIA = [
    r"só que não", r"\baham\b", r"\bsei\.\.\.\b", r"super empolgado", r"mal posso esperar",
    r"tá bom então", r"imagina", r"claro que sim", r"isso com certeza vai funcionar"
]

# Frases que sugerem hesitação ou disfarce de dúvida
PADROES_DUVIDA_DISFARCADA = [
    r"\bse funcionar\b", r"\bacho que sim\b", r"\bvou ver\b", r"\bdepois eu vejo\b",
    r"\bqualquer coisa eu volto\b", r"\bvou pensar\b", r"\bnão sei ainda\b"
]


def detectar_sinais_ambiguidade(mensagem: str) -> Tuple[bool, Optional[str]]:
    """
    Analisa a mensagem do usuário em busca de indícios de ambiguidade, como ironia ou hesitação.

    Args:
        mensagem (str): Texto mais recente do lead.

    Returns:
        Tuple[bool, Optional[str]]: 
            - True se houver ambiguidade detectada.
            - Uma justificativa textual com o tipo e o padrão identificado (ou None).
    """
    texto = mensagem.lower()

    for padrao in PADROES_IRONIA:
        if re.search(padrao, texto):
            return True, f"😏 Ironia identificada: \"{padrao}\""

    for padrao in PADROES_DUVIDA_DISFARCADA:
        if re.search(padrao, texto):
            return True, f"🤔 Hesitação identificada: \"{padrao}\""

    return False, None
