from unidecode import unidecode
from difflib import SequenceMatcher
from typing import Tuple, Optional

# Lista sequencial das etapas da jornada do cliente
ETAPAS_JORNADA = [
    "abordagem_inicial",
    "conexao_profunda",
    "entendimento_dor",
    "antecipou_objecao",
    "apresentou_produto",
    "prova_social",
    "apresentou_valor",
    "reforco_beneficio_personalizado",
    "validou_oferta",
    "comparou_kits",
    "verificou_duvidas",
    "recomendacao_final_fechamento",
    "confirmacao_resumo_pedido",
    "coleta_dados_pessoais",
    "coleta_endereco",
    "forma_pagamento",
    "aguardando_pagamento",
    "pagamento_realizado",
    "pos_venda",
    "encerramento",
    "reengajamento",
    "recuperacao_fluxo"
]

# Padrões que caracterizam cada etapa
PADROES_ETAPA = {
    "abordagem_inicial": ["bem-vinda", "oi", "ola", "graziela"],
    "conexao_profunda": ["me conta", "imagino", "dia a dia", "atividades simples", "realmente dificil"],
    "entendimento_dor": ["me conta melhor", "desde quando sente", "impacta sua rotina", "isso deve atrapalhar bastante"],
    "antecipou_objecao": ["e uma duvida super comum", "imagino que ja tenha tentado outras coisas", "vamos juntas entender se faz sentido"],
    "apresentou_produto": ["facil de usar", "ingredientes naturais"],
    "prova_social": ["mais de 60 mil clientes", "nota 9.2 no reclame aqui", "muita gente sente alivio nos primeiros dias"],
    "apresentou_valor": ["com base no que voce compartilhou", "vou te mostrar os kits", "deixa eu te apresentar as opcoes"],
    "reforco_beneficio_personalizado": ["esse costuma trazer resultado mais rapido", "costuma aliviar mais rapido", "compensa mais no valor por unidade", "reforco"],
    "validou_oferta": ["faz sentido pra voce", "entendi o que voce precisa", "essa opcao pode ser ideal pra sua realidade"],
    "comparou_kits": ["vou te mostrar as diferencas", "vamos comparar os kits", "diferenca entre eles"],
    "verificou_duvidas": ["ficou alguma duvida", "posso esclarecer algo", "te ajudo com mais alguma coisa"],
    "recomendacao_final_fechamento": ["entao vamos garantir", "vamos fechar com esse", "esse kit e um dos mais escolhidos"],
    "confirmacao_resumo_pedido": ["fechamos assim entao", "resumo do seu pedido", "confirmando tudo certinho"],
    "coleta_dados_pessoais": ["vou precisar de alguns dados seus", "nome completo", "telefone com ddd", "algum e-mail pra envio do codigo"],
    "coleta_endereco": ["preciso do seu endereco completo", "cep", "bairro", "complemento opcional"],
    "forma_pagamento": ["prefere pix a vista", "ou cartao em ate 12x", "te passo os dados de pagamento"],
    "aguardando_pagamento": ["assim que fizer o pagamento", "pode me mandar o comprovante", "ainda aguardando o pagamento"],
    "pagamento_realizado": ["ja recebi seu comprovante", "pagamento confirmado", "ja esta tudo certo"],
    "pos_venda": ["envio sera feito em ate", "rastreio sera enviado", "qualquer duvida com a entrega"],
    "encerramento": ["foi um prazer te atender", "qualquer coisa e so me chamar", "obrigado pela confianca"],
    "reengajamento": ["vamos retomar de onde paramos", "desculpa a demora", "continuando nosso atendimento"],
    "recuperacao_fluxo": ["podemos seguir de onde paramos", "vamos continuar de onde parou", "retomando nossa conversa"]
}

def etapa_valida(etapa: str) -> bool:
    return etapa in ETAPAS_JORNADA

def identificar_etapa_jornada(mensagem: str) -> Tuple[str, str]:
    msg = unidecode(mensagem.lower())
    melhor_etapa = "abordagem_inicial"
    melhor_score = 0.0
    melhor_padrao = ""

    for etapa, padroes in PADROES_ETAPA.items():
        for padrao in padroes:
            padrao_normalizado = unidecode(padrao.lower())
            if padrao_normalizado in msg:
                return etapa, f"🔎 Padrão identificado: '{padrao}'"
            score = SequenceMatcher(None, msg, padrao_normalizado).ratio()
            if score > 0.70 and score > melhor_score:
                melhor_score = score
                melhor_etapa = etapa
                melhor_padrao = padrao

    return melhor_etapa, (f"🤏 Similaridade detectada: '{melhor_padrao}' (score {melhor_score:.2f})" if melhor_padrao else "")
