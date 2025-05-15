import os
import openai

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def gerar_resposta(prompt: list[dict], temperatura: float = 0.5, max_tokens: int = 300, modelo: str = "gpt-4o") -> str | None:
    """
    Envia um prompt para o modelo do OpenAI e retorna a resposta formatada.

    Args:
        prompt (list[dict]): Lista de mensagens no formato OpenAI Chat.
        temperatura (float): Grau de criatividade da resposta.
        max_tokens (int): Máximo de tokens para a resposta.
        modelo (str): Nome do modelo OpenAI a ser usado.

    Returns:
        str | None: Resposta gerada ou None em caso de falha.
    """
    try:
        resposta = client.chat.completions.create(
            model=modelo,
            messages=prompt,
            temperature=temperatura,
            max_tokens=max_tokens
        )
        return resposta.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Erro ao gerar resposta do OpenAI: {e}")
        return None

def resumir_texto(historico: str, modelo: str = "gpt-4o") -> str:
    """
    Resume o histórico da conversa para manter o contexto leve e eficiente.

    Args:
        historico (str): Histórico textual completo da conversa.
        modelo (str): Modelo OpenAI usado para resumir.

    Returns:
        str: Texto resumido ou os últimos 3000 caracteres em caso de erro.
    """
    try:
        prompt = [
            {
                "role": "system",
                "content": "Você é uma IA especialista em resumos. Resuma de forma clara, mantendo os pontos importantes, decisões e o tom emocional do cliente."
            },
            {
                "role": "user",
                "content": historico
            }
        ]
        return gerar_resposta(prompt, temperatura=0.3, max_tokens=300, modelo=modelo) or historico[-3000:]
    except Exception as e:
        print(f"❌ Erro ao resumir texto: {e}")
        return historico[-3000:]
