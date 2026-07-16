import re
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("META_TOKEN")
PHONE_ID = os.getenv("PHONE_NUMBER_ID")

ubicaciones = {}

def enviar_mensaje(numero, texto):
    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto}
    }
    requests.post(url, headers=headers, json=body)

def extraer_coordenadas(texto):
    patrones = [
        r"@(-?\d+\.\d+),(-?\d+\.\d+)",
        r"q=(-?\d+\.\d+),(-?\d+\.\d+)",
        r"ll=(-?\d+\.\d+),(-?\d+\.\d+)",
    ]
    for patron in patrones:
        match = re.search(patron, texto)
        if match:
            return float(match.group(1)), float(match.group(2))
    return None

def construir_ruta(coordenadas):
    origen = "22.157963, -100.907335"  # coordenadas del restaurante, cambia esto
    waypoints = "|".join([f"{lat},{lng}" for lat, lng in coordenadas[:-1]])
    destino = f"{coordenadas[-1][0]},{coordenadas[-1][1]}"

    url = (
        f"https://www.google.com/maps/dir/{origen}/"
        + "/".join([f"{lat},{lng}" for lat, lng in coordenadas])
        + f"/{origen}"
    )
    return url

def procesar(numero, texto):
    texto = texto.strip()

    if texto.lower() == "listo":
        if numero not in ubicaciones or len(ubicaciones[numero]) == 0:
            enviar_mensaje(numero, "No tengo ninguna ubicación guardada. Mándame los links primero.")
            return
        coords = ubicaciones[numero]
        ruta = construir_ruta(coords)
        n = len(coords)
        enviar_mensaje(numero, f"Ruta lista con {n} parada(s):\n{ruta}")
        ubicaciones[numero] = []
        return

    if texto.lower() == "cancelar":
        ubicaciones[numero] = []
        enviar_mensaje(numero, "Ubicaciones borradas. Puedes empezar de nuevo.")
        return

    coords = extraer_coordenadas(texto)
    if coords:
        if numero not in ubicaciones:
            ubicaciones[numero] = []
        ubicaciones[numero].append(coords)
        n = len(ubicaciones[numero])
        enviar_mensaje(numero, f"Ubicación {n} guardada. Manda otra o escribe *listo* para generar la ruta.")
    else:
        enviar_mensaje(numero, "No reconocí una ubicación de Google Maps. Manda el link completo.")