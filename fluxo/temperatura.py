from typing import Optional, Tuple
from difflib import SequenceMatcher

# Temperaturas ordenadas do menos para o mais quente
NIVEIS_TEMPERATURA = ["frio", "morno", "quente"]

# Frases típicas que indicam o grau de intenção de compra
MAPA_TEMPERATURA = {
    "frio": [
        "só estou olhando", "só pesquisando", "vi por acaso", "curioso", "só queria saber", "não sei ainda"
    ],
    "morno": [
        "quanto custa", "tem desconto", "parece bom", "vou pensar", "interessante", "como funciona", "vale a pena?"
    ],
    "quente": [
        "quero comprar", "já quero", "me manda o link", "aceita pix", "fechar agora", "já decidi", "como finalizo"
    ]
}

def similar(a: str, b: str) -> float:
    """Calcula a similaridade entre duas frases."""
    return SequenceMatcher(None, a, b).ratio()

def classificar_temperatura(mensagem: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Classifica a temperatura do lead com base apenas na mensagem.
    Gera uma hipótese e uma justificativa textual (match ou aproximação).
    """
    texto = mensagem.lower()
    melhor_nivel = None
    melhor_score = 0.0
    justificativa = None

    for nivel in reversed(NIVEIS_TEMPERATURA):  # Começa do mais quente
        for padrao in MAPA_TEMPERATURA[nivel]:
            if padrao in texto:
                return nivel, f"🔥 Frase identificada: \"{padrao}\""
            score = similar(padrao, texto)
            if score > 0.78 and score > melhor_score:
                melhor_score = score
                melhor_nivel = nivel
                justificativa = f"♨️ Frase semelhante: \"{padrao}\" (similaridade {score:.2f})"

    return (melhor_nivel, justificativa) if melhor_nivel else (None, None)
