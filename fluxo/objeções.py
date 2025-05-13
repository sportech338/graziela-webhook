from typing import Optional

OBJECOES_ATIVAS = {
    "objecao_valor": [
        "tá caro", "muito caro", "não tenho dinheiro", "sem grana"
    ],
    "objecao_confianca": [
        "nunca ouvi falar", "é seguro?", "isso é confiável"
    ],
    "objecao_resultado": [
        "isso funciona mesmo", "tem prova?", "funciona de verdade"
    ],
    "objecao_entrega": [
        "demora pra chegar", "moro longe", "entrega demora"
    ],
    "objecao_garantia": [
        "posso devolver", "tem garantia"
    ],
    "objecao_composicao": [
        "o que tem nele", "composição", "contra indicação"
    ],
    "objecao_forma_pagamento": [
        "não uso pix", "só tenho boleto", "não tenho cartão"
    ],
    "objecao_familia": [
        "vou falar com meu marido", "minha mãe não deixa", "vou ver com meu pai"
    ],
    "objecao_gravidez": [
        "estou grávida", "posso usar grávida"
    ]
}

EVASIVAS = {
    "evasiva_vou_pensar": [
        "vou pensar", "te aviso depois", "vou decidir"
    ],
    "evasiva_sem_resposta": [
        "..."  # placeholder para ausência
    ],
    "evasiva_preciso_ver_com_alguem": [
        "vou ver com minha esposa", "vou falar com meu médico"
    ],
    "evasiva_esperar_salario": [
        "recebo semana que vem", "esperar meu pagamento", "salário cai dia"
    ],
    "evasiva_desconfianca": [
        "tem muita coisa falsa", "não confio muito"
    ],
    "evasiva_teste_primeiro": [
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
