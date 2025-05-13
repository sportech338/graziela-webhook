from flask import Flask
from fluxo.webhook import webhook_bp

app = Flask(__name__)

# Registra o Blueprint de rotas
app.register_blueprint(webhook_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
