from typing import Optional, Tuple
from difflib import SequenceMatcher

CONSCIENCIA_MAPA = {
    "inconsciente": [
        "não sei do que se trata", "nem sei o que é isso", "não entendi",
        "que produto é esse?", "do que se trata"
    ],
    "problema_consciente": [
        "tenho dores", "me sinto cansado", "tô com dificuldade",
        "não estou bem", "preciso de ajuda com meu corpo"
    ],
    "solucao_consciente": [
        "isso pode ajudar", "me falaram que resolve", "existe algo pra isso",
        "o que resolve isso"
    ],
    "produto_consciente": [
        "já ouvi falar", "vi no instagram", "conheço esse produto",
        "alguém me indicou"
    ],
    "pronto_para_compra": [
        "quero agora", "como faço pra comprar", "me manda o link",
        "aceita pix", "passa o valor"
    ]
}

def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def classificar_consciencia(mensagem: str, contexto: Optional[str] = "") -> Tuple[Optional[str], Optional[str]]:
    texto = (mensagem + " " + (contexto or "")).lower()
    melhor_nivel = None
    melhor_score = 0.0
    justificativa = None

    for nivel, padroes in CONSCIENCIA_MAPA.items():
        for padrao in padroes:
            padrao_lower = padrao.lower()
            if padrao_lower in texto:
                return nivel, f"🔎 Frase identificada: \"{padrao}\""
            score = similar(padrao_lower, texto)
            if score > 0.75 and score > melhor_score:
                melhor_score = score
                melhor_nivel = nivel
                justificativa = f"🤏 Frase semelhante: \"{padrao}\" (similaridade {score:.2f})"

    return (melhor_nivel, justificativa) if melhor_nivel else (None, None)
