import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import base64

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SPREADSHEET_NAME = "Histórico de conversas | Graziela"

def criar_arquivo_credenciais():
    try:
        encoded = os.environ.get("GOOGLE_CREDENTIALS_BASE64")
        if not encoded:
            raise ValueError("Variável GOOGLE_CREDENTIALS_BASE64 não encontrada.")
        decoded = base64.b64decode(encoded).decode("utf-8")
        with open("credentials.json", "w") as f:
            f.write(decoded)
        print("🔐 Arquivo credentials.json criado com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao criar credentials.json: {e}")

if not os.path.exists("credentials.json"):
    criar_arquivo_credenciais()

def registrar_no_sheets(telefone, mensagem, resposta):
    try:
        creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
        gc = gspread.authorize(creds)
        sheet = gc.open(SPREADSHEET_NAME).sheet1
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        sheet.append_row([telefone, mensagem, resposta, agora])
        print("📄 Conversa registrada no Google Sheets.")
    except Exception as e:
        print(f"❌ Erro ao registrar no Google Sheets: {e}")
