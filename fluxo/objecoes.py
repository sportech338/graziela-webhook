from typing import Optional

OBJECOES_ATIVAS = {
    "Preço": [
        "tá caro", "muito caro", "não tenho dinheiro", "sem grana"
    ],
    "Confiança": [
        "nunca ouvi falar", "é seguro?", "isso é confiável"
    ],
    "Eficácia": [
        "isso funciona mesmo", "tem prova?", "funciona de verdade"
    ],
    "Entrega": [
        "demora pra chegar", "moro longe", "entrega demora"
    ],
    "Garantia": [
        "posso devolver", "tem garantia"
    ],
    "Composição": [
        "o que tem nele", "composição", "contra indicação"
    ],
    "Forma de pagamento": [
        "não uso pix", "só tenho boleto", "não tenho cartão"
    ],
    "Família": [
        "vou falar com meu marido", "minha mãe não deixa", "vou ver com meu pai"
    ],
    "Gravidez": [
        "estou grávida", "posso usar grávida"
    ]
}

EVASIVAS = {
    "evasiva_vou_pensar": [
        "Vou pensar", "te aviso depois", "vou decidir"
    ],
    "Sem resposta": [
        "..."  # placeholder para ausência
    ],
    "Preciso ver com alguém": [
        "vou ver com minha esposa", "vou falar com meu médico"
    ],
    "Esperar salário": [
        "recebo semana que vem", "esperar meu pagamento", "salário cai dia"
    ],
    "Desconfiança": [
        "tem muita coisa falsa", "não confio muito"
    ],
    "Teste primeiro": [
        "posso comprar só um", "testar primeiro", "ver se funciona primeiro"
    ]
}


def identificar_objecao(mensagem: str) -> Optional[str]:
    msg = mensagem.lower()

    for tipo, padroes in OBJECOES_ATIVAS.items():
        if any(p in msg for p in padroes):
            return tipo

    for tipo, padroes in EVASIVAS.items():
        if any(p in msg for p in padroes):
            return tipo

    return None
