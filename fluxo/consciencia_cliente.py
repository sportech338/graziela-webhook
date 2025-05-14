from typing import Optional

# Mapa de padrões para cada nível de consciência
CONSCIENCIA_MAPA = {
    "Incosciente do produto": [
        "não sei do que se trata", "nem sei o que é isso", "não entendi",
        "que produto é esse?", "do que se trata?"
    ],
    "Consciente do problema": [
        "tenho dores", "me sinto cansado", "tô com dificuldade",
        "não estou bem", "preciso de ajuda com meu corpo"
    ],
    "Consciente da solução": [
        "isso pode ajudar?", "me falaram que resolve", "existe algo pra isso?",
        "o que resolve isso?"
    ],
    "Consciente do produto": [
        "já ouvi falar", "vi no Instagram", "conheço esse produto",
        "alguém me indicou"
    ],
    "Pronto para comprar": [
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
