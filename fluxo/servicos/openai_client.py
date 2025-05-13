import os
import openai

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def gerar_resposta(prompt, temperatura=0.5, max_tokens=300, modelo="gpt-4o"):
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
    try:
        prompt = [
            {"role": "system", "content": "Resuma com clareza e sem perder contexto..."},
            {"role": "user", "content": historico}
        ]
        return gerar_resposta(prompt, temperatura=0.3, max_tokens=300, modelo=modelo)
    except Exception as e:
        print(f"❌ Erro ao resumir texto: {e}")
        return historico[-3000:]
