from typing import Optional
from difflib import SequenceMatcher

# Mapa de padrões para cada nível de consciência
CONSCIENCIA_MAPA = {
    "inconsciente": [
        "não sei do que se trata", "nem sei o que é isso", "não entendi",
        "que produto é esse?", "do que se trata?"
    ],
    "problema_consciente": [
        "tenho dores", "me sinto cansado", "tô com dificuldade",
        "não estou bem", "preciso de ajuda com meu corpo"
    ],
    "solucao_consciente": [
        "isso pode ajudar?", "me falaram que resolve", "existe algo pra isso?",
        "o que resolve isso?"
    ],
    "produto_consciente": [
        "já ouvi falar", "vi no instagram", "conheço esse produto",
        "alguém me indicou"
    ],
    "pronto_para_compra": [
        "quero agora", "como faço pra comprar?", "me manda o link",
        "aceita pix?", "passa o valor"
    ]
}

def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def classificar_consciencia(mensagem: str, contexto: Optional[str] = "") -> Optional[str]:
    texto = (mensagem + " " + contexto).lower()
    melhor_nivel = None
    melhor_score = 0.0

    for nivel, padroes in CONSCIENCIA_MAPA.items():
        for padrao in padroes:
            if padrao in texto:
                return nivel  # 🎯 Match exato
            score = similar(padrao, texto)
            if score > 0.75 and score > melhor_score:
                melhor_score = score
                melhor_nivel = nivel

    return melhor_nivel if melhor_score >= 0.75 else None
