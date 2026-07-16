from flask import Flask, request
from dotenv import load_dotenv
import os
import bot

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        return challenge, 200
    return "Token inválido", 403

@app.route("/webhook", methods=["POST"])
def recibir_mensaje():
    data = request.get_json()
    try:
        mensajes = data["entry"][0]["changes"][0]["value"]["messages"]
        for mensaje in mensajes:
            numero = mensaje["from"]
            texto = mensaje.get("text", {}).get("body", "")
            bot.procesar(numero, texto)
    except (KeyError, IndexError):
        pass
    return "ok", 200

if __name__ == "__main__":
    app.run(port=5000)