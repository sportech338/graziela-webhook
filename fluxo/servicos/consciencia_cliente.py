from typing import Optional

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
        "já ouvi falar", "vi no Instagram", "conheço esse produto",
        "alguém me indicou"
    ],
    "pronto_para_compra": [
        "quero agora", "como faço pra comprar?", "me manda o link",
        "aceita pix?", "passa o valor"
    ]
}

def classificar_consciencia(mensagem: str) -> Optional[str]:
    msg = mensagem.lower()
    for nivel, padroes in CONSCIENCIA_MAPA.items():
        if any(p in msg for p in padroes):
            return nivel
    return None
