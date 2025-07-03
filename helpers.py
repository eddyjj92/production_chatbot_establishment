from typing import Optional, Dict, Union, List
import requests


def get_establishment(establishment_id, token) -> Optional[Dict]:
    url = f"https://backend.clapzy.pro/api/establishments/{establishment_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanza excepción para códigos 4XX/5XX

        # Obtener la respuesta completa como diccionario
        data = response.json()

        return data["establishment"]

    except requests.exceptions.RequestException as e:
        print(f"Error en la petición: {e}")
        return {"error": "No se pudo obtener información del establecimiento", "details": str(e)}

    except Exception as e:
        print(f"Error inesperado: {e}")
        return {"error": "Error inesperado", "details": str(e)}


def get_establishments(token) -> Union[List[Dict], Dict[str, str]]:
    url = f"https://backend.clapzy.pro/api/establishments?per_page=100&page=1"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanza excepción para códigos 4XX/5XX

        # Obtener la respuesta completa como diccionario
        data = response.json()

        return data["establishments"]

    except requests.exceptions.RequestException as e:
        print(f"Error en la petición: {e}")
        return {"error": "No se pudo obtener los establecimiento", "details": str(e)}

    except Exception as e:
        print(f"Error inesperado: {e}")
        return {"error": "Error inesperado", "details": str(e)}


import random

def get_greeting_message():
    greetings = [
        "¡Hola! Bienvenido/a. ¿En qué puedo ayudarte hoy?",
        "¡Buen día! Estoy aquí para asistirte, ¿cómo puedo servirte?",
        "¡Bienvenido/a! Me alegra tenerte por aquí. ¿Qué necesitas?",
        "¿Listo/a para empezar? ¡Estoy aquí para ayudarte!",
        "¡Hola de nuevo! ¿En qué puedo colaborarte hoy?",
        "¡Muy buenas! Soy tu asistente virtual. ¿Qué puedo hacer por ti?",
        "¡Encantado/a de verte! Cuéntame, ¿en qué puedo ayudarte?",
        "¡Saludos! ¿Qué planes tienes para hoy? Yo estoy listo/a para ayudarte.",
        "¡Bienvenido/a! Si necesitas algo, solo dime.",
        "¡Hola! Estoy aquí para lo que necesites. ¿Por dónde empezamos?"
    ]
    return random.choice(greetings)
