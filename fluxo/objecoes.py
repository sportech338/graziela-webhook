from typing import Optional, Tuple

# Objeções diretas e explícitas
OBJECOES_ATIVAS = {
    "Preço": [
        "tá caro", "muito caro", "não tenho dinheiro", "sem grana", "não posso pagar"
    ],
    "Confiança": [
        "nunca ouvi falar", "é seguro?", "isso é confiável", "parece golpe"
    ],
    "Eficácia": [
        "isso funciona mesmo", "tem prova?", "funciona de verdade", "tem garantia que resolve?"
    ],
    "Entrega": [
        "demora pra chegar", "moro longe", "entrega demora", "e o frete?"
    ],
    "Garantia": [
        "posso devolver", "tem garantia", "e se eu não gostar?"
    ],
    "Composição": [
        "o que tem nele", "composição", "contra indicação", "tem glúten?"
    ],
    "Forma de pagamento": [
        "não uso pix", "só tenho boleto", "não tenho cartão", "parcelar?"
    ],
    "Família": [
        "vou falar com meu marido", "minha mãe não deixa", "vou ver com meu pai"
    ],
    "Gravidez": [
        "estou grávida", "posso usar grávida", "grávida pode usar?"
    ]
}

# Evasivas comuns que sugerem hesitação
EVASIVAS = {
    "Evasiva: Vou pensar": [
        "vou pensar", "te aviso depois", "vou decidir", "depois eu vejo"
    ],
    "Evasiva: Preciso consultar alguém": [
        "vou ver com minha esposa", "vou falar com meu médico", "preciso conversar com alguém"
    ],
    "Evasiva: Esperar salário": [
        "recebo semana que vem", "esperar meu pagamento", "salário cai dia"
    ],
    "Evasiva: Testar primeiro": [
        "posso comprar só um", "testar primeiro", "ver se funciona primeiro"
    ],
    "Evasiva: Desconfiança": [
        "tem muita coisa falsa", "não confio muito", "parece bom demais"
    ],
    "Evasiva: Silêncio": [
        "..."  # ausência de resposta direta
    ]
}


def identificar_objecao(mensagem: str) -> Tuple[Optional[str], Optional[str]]:
    texto = mensagem.lower()

    for tipo, padroes in OBJECOES_ATIVAS.items():
        for padrao in padroes:
            if padrao in texto:
                return tipo, f"🚫 Objeção direta identificada: \"{padrao}\""

    for tipo, padroes in EVASIVAS.items():
        for padrao in padroes:
            if padrao in texto:
                return tipo, f"🌀 Evasiva detectada: \"{padrao}\""

    return None, None
