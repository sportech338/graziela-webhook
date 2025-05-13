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

def etapa_valida(etapa: str) -> bool:
    return etapa in ETAPAS_JORNADA

def identificar_etapa_jornada(mensagem: str) -> str:
    msg = mensagem.lower()

    if any(p in msg for p in ["bem-vinda", "oi", "olá", "Graziela"]):
        return "abordagem_inicial"

    if any(p in msg for p in ["Me conta", "Imagino", "dia a dia", "atividades simples", "realmente difícil"]):
        return "conexao_profunda"

    if any(p in msg for p in ["me conta melhor", "desde quando sente", "impacta sua rotina", "isso deve atrapalhar bastante"]):
        return "entendimento_dor"

    if any(p in msg for p in ["é uma dúvida super comum", "imagino que já tenha tentado outras coisas", "vamos juntas entender se faz sentido"]):
        return "antecipou_objecao"

    if any(p in msg for p in ["fácil de usar", "ingredientes naturais"]):
        return "apresentou_produto"

    if any(p in msg for p in ["mais de 60 mil clientes", "nota 9.2 no reclame aqui", "muita gente sente alívio nos primeiros dias"]):
        return "prova_social"

    if any(p in msg for p in ["com base no que você compartilhou", "vou te mostrar os kits", "deixa eu te apresentar as opções"]):
        return "apresentou_valor"

    if any(p in msg for p in ["esse costuma trazer resultado mais rápido", "costuma aliviar mais rápido", "compensa mais no valor por unidade", "reforço"]):
        return "reforco_beneficio_personalizado"

    if any(p in msg for p in ["faz sentido pra você", "entendi o que você precisa", "essa opção pode ser ideal pra sua realidade"]):
        return "validou_oferta"

    if any(p in msg for p in ["vou te mostrar as diferenças", "vamos comparar os kits", "diferença entre eles"]):
        return "comparou_kits"

    if any(p in msg for p in ["ficou alguma dúvida", "posso esclarecer algo", "te ajudo com mais alguma coisa"]):
        return "verificou_duvidas"

    if any(p in msg for p in ["então vamos garantir", "vamos fechar com esse", "esse kit é um dos mais escolhidos"]):
        return "recomendacao_final_fechamento"

    if any(p in msg for p in ["fechamos assim então", "resumo do seu pedido", "confirmando tudo certinho"]):
        return "confirmacao_resumo_pedido"

    if any(p in msg for p in ["vou precisar de alguns dados seus", "nome completo", "telefone com ddd", "algum e-mail pra envio do código"]):
        return "coleta_dados_pessoais"

    if any(p in msg for p in ["preciso do seu endereço completo", "cep", "bairro", "complemento opcional"]):
        return "coleta_endereco"

    if any(p in msg for p in ["prefere pix à vista", "ou cartão em até 12x", "te passo os dados de pagamento"]):
        return "forma_pagamento"

    if any(p in msg for p in ["assim que fizer o pagamento", "pode me mandar o comprovante", "ainda aguardando o pagamento"]):
        return "aguardando_pagamento"

    if any(p in msg for p in ["já recebi seu comprovante", "pagamento confirmado", "já está tudo certo"]):
        return "pagamento_realizado"

    if any(p in msg for p in ["envio será feito em até", "rastreio será enviado", "qualquer dúvida com a entrega"]):
        return "pos_venda"

    if any(p in msg for p in ["foi um prazer te atender", "qualquer coisa é só me chamar", "obrigado pela confiança"]):
        return "encerramento"

    if any(p in msg for p in ["vamos retomar de onde paramos", "desculpa a demora", "continuando nosso atendimento"]):
        return "reengajamento"

    if any(p in msg for p in ["podemos seguir de onde paramos", "vamos continuar de onde parou", "retomando nossa conversa"]):
        return "recuperacao_fluxo"

    return "abordagem_inicial"
