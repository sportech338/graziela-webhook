from typing import Optional, Tuple
from difflib import SequenceMatcher

# Etapas ajustadas para refletir melhor a jornada real do lead
CONSCIENCIA_MAPA = {
    "inconsciente": [
        "não sei do que se trata", "nem sei o que é isso", "não entendi direito",
        "isso é o quê?", "que produto é esse", "do que se trata"
    ],
    "problema_consciente": [
        "tenho dores", "sinto dor", "me sinto cansado", "tô com dificuldade",
        "não estou bem", "tô com problema no corpo", "preciso de ajuda com minha saúde"
    ],
    "solucao_consciente": [
        "isso pode ajudar", "me falaram que resolve", "existe algo pra isso",
        "tem alguma solução", "o que resolve isso", "funciona pra isso"
    ],
    "produto_consciente": [
        "já ouvi falar", "vi no instagram", "conheço esse produto",
        "alguém me indicou", "amiga minha usou", "acho que já vi"
    ],
    "pronto_para_compra": [
        "quero agora", "como faço pra comprar", "me manda o link",
        "aceita pix", "passa o valor", "fechar agora", "já quero"
    ]
}

def similar(a: str, b: str) -> float:
    """Calcula similaridade entre duas frases."""
    return SequenceMatcher(None, a, b).ratio()

def classificar_consciencia(mensagem: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Retorna o nível de consciência e uma justificativa textual.
    Não define com certeza — apenas gera uma hipótese com base na mensagem.
    """
    texto = mensagem.lower()
    melhor_nivel = None
    melhor_score = 0.0
    justificativa = None

    for nivel, padroes in CONSCIENCIA_MAPA.items():
        for padrao in padroes:
            padrao_lower = padrao.lower()
            if padrao_lower in texto:
                return nivel, f"🔎 Frase identificada: \"{padrao}\""
            score = similar(padrao_lower, texto)
            if score > 0.78 and score > melhor_score:
                melhor_score = score
                melhor_nivel = nivel
                justificativa = f"🤏 Frase semelhante a \"{padrao}\" (similaridade {score:.2f})"

    return (melhor_nivel, justificativa) if melhor_nivel else (None, None)
