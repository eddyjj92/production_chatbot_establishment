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
