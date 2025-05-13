from unidecode import unidecode

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

# Verifica se uma etapa é válida
def etapa_valida(etapa: str) -> bool:
    return etapa in ETAPAS_JORNADA

# Identifica a etapa da jornada com base em padrões da resposta da Graziela
def identificar_etapa_jornada(mensagem: str) -> str:
    msg = unidecode(mensagem.lower())

    if any(p in msg for p in ["bem-vinda", "oi", "ola", "graziela"]):
        return "abordagem_inicial"

    if any(p in msg for p in ["me conta", "imagino", "dia a dia", "atividades simples", "realmente dificil"]):
        return "conexao_profunda"

    if any(p in msg for p in ["me conta melhor", "desde quando sente", "impacta sua rotina", "isso deve atrapalhar bastante"]):
        return "entendimento_dor"

    if any(p in msg for p in ["e uma duvida super comum", "imagino que ja tenha tentado outras coisas", "vamos juntas entender se faz sentido"]):
        return "antecipou_objecao"

    if any(p in msg for p in ["facil de usar", "ingredientes naturais"]):
        return "apresentou_produto"

    if any(p in msg for p in ["mais de 60 mil clientes", "nota 9.2 no reclame aqui", "muita gente sente alivio nos primeiros dias"]):
        return "prova_social"

    if any(p in msg for p in ["com base no que voce compartilhou", "vou te mostrar os kits", "deixa eu te apresentar as opcoes"]):
        return "apresentou_valor"

    if any(p in msg for p in ["esse costuma trazer resultado mais rapido", "costuma aliviar mais rapido", "compensa mais no valor por unidade", "reforco"]):
        return "reforco_beneficio_personalizado"

    if any(p in msg for p in ["faz sentido pra voce", "entendi o que voce precisa", "essa opcao pode ser ideal pra sua realidade"]):
        return "validou_oferta"

    if any(p in msg for p in ["vou te mostrar as diferencas", "vamos comparar os kits", "diferenca entre eles"]):
        return "comparou_kits"

    if any(p in msg for p in ["ficou alguma duvida", "posso esclarecer algo", "te ajudo com mais alguma coisa"]):
        return "verificou_duvidas"

    if any(p in msg for p in ["entao vamos garantir", "vamos fechar com esse", "esse kit e um dos mais escolhidos"]):
        return "recomendacao_final_fechamento"

    if any(p in msg for p in ["fechamos assim entao", "resumo do seu pedido", "confirmando tudo certinho"]):
        return "confirmacao_resumo_pedido"

    if any(p in msg for p in ["vou precisar de alguns dados seus", "nome completo", "telefone com ddd", "algum e-mail pra envio do codigo"]):
        return "coleta_dados_pessoais"

    if any(p in msg for p in ["preciso do seu endereco completo", "cep", "bairro", "complemento opcional"]):
        return "coleta_endereco"

    if any(p in msg for p in ["prefere pix a vista", "ou cartao em ate 12x", "te passo os dados de pagamento"]):
        return "forma_pagamento"

    if any(p in msg for p in ["assim que fizer o pagamento", "pode me mandar o comprovante", "ainda aguardando o pagamento"]):
        return "aguardando_pagamento"

    if any(p in msg for p in ["ja recebi seu comprovante", "pagamento confirmado", "ja esta tudo certo"]):
        return "pagamento_realizado"

    if any(p in msg for p in ["envio sera feito em ate", "rastreio sera enviado", "qualquer duvida com a entrega"]):
        return "pos_venda"

    if any(p in msg for p in ["foi um prazer te atender", "qualquer coisa e so me chamar", "obrigado pela confianca"]):
        return "encerramento"

    if any(p in msg for p in ["vamos retomar de onde paramos", "desculpa a demora", "continuando nosso atendimento"]):
        return "reengajamento"

    if any(p in msg for p in ["podemos seguir de onde paramos", "vamos continuar de onde parou", "retomando nossa conversa"]):
        return "recuperacao_fluxo"

    return "abordagem_inicial"
