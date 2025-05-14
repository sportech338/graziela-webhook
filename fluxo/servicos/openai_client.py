import os
import openai

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def gerar_resposta(prompt, temperatura=0.5, max_tokens=300, modelo="gpt-4o"):
    """
    Envia um prompt para o modelo do OpenAI e retorna a resposta formatada.
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

def resumir_texto(historico, modelo="gpt-4o"):
    """
    Resume o histórico da conversa para manter o contexto leve e eficiente.
    """
    try:
        prompt = [
            {"role": "system", "content": "Você é uma IA especialista em resumos. Resuma de forma clara, mantendo os pontos importantes, as decisões e o tom emocional do cliente."},
            {"role": "user", "content": historico}
        ]
        return gerar_resposta(prompt, temperatura=0.3, max_tokens=300, modelo=modelo)
    except Exception as e:
        print(f"❌ Erro ao resumir texto: {e}")
        return historico[-3000:]
