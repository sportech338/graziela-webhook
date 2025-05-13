import os
import requests

def baixar_audio_do_meta(media_id):
    try:
        token = os.environ["WHATSAPP_TOKEN"]
        url_info = f"https://graph.facebook.com/v18.0/{media_id}"
        headers = {"Authorization": f"Bearer {token}"}
        file_url = requests.get(url_info, headers=headers).json()["url"]
        res_audio = requests.get(file_url, headers=headers)
        return res_audio.content
    except Exception as e:
        print(f"❌ Erro ao baixar áudio: {e}")
        return None

def transcrever_audio(blob):
    try:
        res = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
            files={"file": ("audio.ogg", blob, "audio/ogg")},
            data={"model": "whisper-1", "language": "pt"}
        )
        if res.status_code != 200 or "text" not in res.json():
            raise Exception("Falha na transcrição.")
        return res.json()["text"]
    except Exception as e:
        print(f"❌ Erro na transcrição de áudio: {e}")
        return None
