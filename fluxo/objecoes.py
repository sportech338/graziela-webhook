from typing import Optional, Tuple
from difflib import SequenceMatcher

OBJECOES_ATIVAS = {
    "Preco": [
        "tá caro", "muito caro", "não tenho dinheiro", "sem grana", "não posso pagar"
    ],
    "Confianca": [
        "nunca ouvi falar", "é seguro?", "isso é confiável", "parece golpe"
    ],
    "Eficacia": [
        "isso funciona mesmo", "tem prova?", "funciona de verdade", "tem garantia que resolve?"
    ],
    "Entrega": [
        "demora pra chegar", "moro longe", "entrega demora", "e o frete?"
    ],
    "Garantia": [
        "posso devolver", "tem garantia", "e se eu não gostar?"
    ],
    "Composicao": [
        "o que tem nele", "composição", "contra indicação", "tem glúten?"
    ],
    "Forma de pagamento": [
        "não uso pix", "só tenho boleto", "não tenho cartão", "parcelar?"
    ],
    "Familia": [
        "vou falar com meu marido", "minha mãe não deixa", "vou ver com meu pai"
    ],
    "Gravidez": [
        "estou grávida", "posso usar grávida", "grávida pode usar?"
    ]
}

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
        "..."
    ]
}

def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def identificar_objecao(mensagem: str) -> Tuple[Optional[str], Optional[str]]:
    texto = mensagem.lower()
    melhor_match = None
    melhor_score = 0.0
    justificativa = None

    for tipo, padroes in {**OBJECOES_ATIVAS, **EVASIVAS}.items():
        for padrao in padroes:
            if padrao in texto:
                return tipo, f"🔍 Padrão identificado: \"{padrao}\""
            score = similar(padrao, texto)
            if score > 0.7 and score > melhor_score:
                melhor_match = tipo
                melhor_score = score
                justificativa = f"🤏 Similaridade com \"{padrao}\" ({score:.2f})"

    return (melhor_match, justificativa) if melhor_match else (None, None)
