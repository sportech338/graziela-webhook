import re
from typing import Optional, Tuple
from difflib import SequenceMatcher

# Padrões que sugerem sarcasmo, ironia ou desdém
PADROES_IRONIA = [
    "só que não", "aham", "sei...", "super empolgado", "mal posso esperar",
    "tá bom então", "imagina", "claro que sim", "isso com certeza vai funcionar"
]

# Padrões que sugerem hesitação ou dúvida disfarçada
PADROES_DUVIDA_DISFARCADA = [
    "se funcionar", "acho que sim", "vou ver", "depois eu vejo",
    "qualquer coisa eu volto", "vou pensar", "não sei ainda"
]

def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def detectar_sinais_ambiguidade(mensagem: str) -> Tuple[bool, Optional[str]]:
    """
    Analisa a mensagem do lead para identificar sinais de ambiguidade: ironia ou hesitação.

    Retorna True e a justificativa se detectar padrão ou similaridade relevante.
    """
    texto = mensagem.lower()

    for padrao in PADROES_IRONIA:
        if padrao in texto:
            return True, f"😏 Indício de ironia identificado: \"{padrao}\""
        score = similar(texto, padrao)
        if score > 0.8:
            return True, f"😏 Ironia provável (similar a \"{padrao}\" – similaridade {score:.2f})"

    for padrao in PADROES_DUVIDA_DISFARCADA:
        if padrao in texto:
            return True, f"🤔 Indício de hesitação identificado: \"{padrao}\""
        score = similar(texto, padrao)
        if score > 0.8:
            return True, f"🤔 Hesitação provável (similar a \"{padrao}\" – similaridade {score:.2f})"

    return False, None
