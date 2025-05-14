import re
from typing import Optional, Tuple

# Padrões que sugerem sarcasmo, ironia ou desdém
PADROES_IRONIA = [
    r"\bsó que não\b", r"\baham\b", r"\bsei\.\.\.\b", r"super empolgado", r"mal posso esperar",
    r"tá bom então", r"\bimagina\b", r"claro que sim", r"isso com certeza vai funcionar"
]

# Padrões que sugerem hesitação ou dúvida disfarçada
PADROES_DUVIDA_DISFARCADA = [
    r"\bse funcionar\b", r"\bacho que sim\b", r"\bvou ver\b", r"\bdepois eu vejo\b",
    r"\bqualquer coisa eu volto\b", r"\bvou pensar\b", r"\bnão sei ainda\b"
]

def detectar_sinais_ambiguidade(mensagem: str) -> Tuple[bool, Optional[str]]:
    """
    Analisa a mensagem do lead para identificar sinais de ambiguidade: ironia ou hesitação.

    Args:
        mensagem (str): Texto mais recente enviado pelo lead.

    Returns:
        Tuple[bool, Optional[str]]: 
            - bool: True se houver ambiguidade (ironia ou hesitação).
            - str: Justificativa textual com tipo e padrão identificado (ou None).
    """
    texto = mensagem.lower()

    for padrao in PADROES_IRONIA:
        if re.search(padrao, texto):
            return True, f"😏 Indício de ironia identificado: \"{padrao}\""

    for padrao in PADROES_DUVIDA_DISFARCADA:
        if re.search(padrao, texto):
            return True, f"🤔 Indício de hesitação identificado: \"{padrao}\""

    return False, None
