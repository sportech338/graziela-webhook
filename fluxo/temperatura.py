from typing import Optional

# Temperaturas ordenadas do menos para o mais quente
NIVEIS_TEMPERATURA = [
    "frio",
    "morno",
    "quente"
]

# Padrões típicos de linguagem associados ao interesse do lead
MAPA_TEMPERATURA = {
    "frio": [
        "só estou olhando", "curioso", "vi por acaso", "só queria saber", "não sei ainda"
    ],
    "morno": [
        "quanto custa", "interessante", "como funciona", "tem desconto", "parece bom", "vou pensar"
    ],
    "quente": [
        "quero comprar", "me manda o link", "aceita pix", "como finalizo", "fechar agora", "já decidi"
    ]
}

def classificar_temperatura(mensagem: str, contexto: str = "") -> Optional[str]:
    """
    Avalia a temperatura do lead com base na mensagem + contexto.
    Começa verificando os sinais mais quentes para garantir assertividade na intenção de compra.
    """
    texto = f"{contexto} {mensagem}".lower()

    for nivel in reversed(NIVEIS_TEMPERATURA):  # Começa do mais quente
        padroes = MAPA_TEMPERATURA[nivel]
        if any(p in texto for p in padroes):
            return nivel

    return None
